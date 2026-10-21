import { describe, it, expect, vi } from 'vitest';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { faseAtual, reservar, preparar, validarPacote, caminhoPermitido, consultar } from '../scripts/creditos-ia.mjs';

const agora = new Date('2026-10-23T12:00:00.000Z');
const vazio = () => ({ version: 1, reservas: [] });
function comRepositorio(testar) {
  const raiz = mkdtempSync(join(tmpdir(), 'pcm-creditos-'));
  const git = (...args) => execFileSync('git', args, { cwd: raiz, encoding: 'utf8' });
  try {
    git('init', '-q');
    mkdirSync(join(raiz, 'src'));
    writeFileSync(join(raiz, 'src/exemplo.js'), 'export const ficticio = true;');
    git('add', '.');
    return testar(raiz, git);
  } finally { rmSync(raiz, { recursive: true, force: true }); }
}
const pacote = () => comRepositorio(raiz => preparar('Conferir exemplo fictício.', 'src/exemplo.js', raiz));

describe('orçamento temporário da API', () => {
  it('bloqueia antes do início e no vencimento, separando as fases pelo horário brasileiro', () => {
    expect(() => faseAtual('2026-10-20T23:59:59Z')).toThrow();
    expect(faseAtual('2026-10-21T00:00:00Z')).toBe('melhorias');
    expect(faseAtual('2026-10-29T02:59:59Z')).toBe('melhorias');
    expect(faseAtual('2026-10-29T03:00:00Z')).toBe('revisao');
    expect(faseAtual('2026-10-31T02:59:59Z')).toBe('revisao');
    expect(() => faseAtual('2026-10-31T03:00:00Z')).toThrow();
    expect(() => faseAtual('inválido')).toThrow();
  });

  it('reserva antes da chamada e impede repetir a mesma execução', () => {
    const ledger = reservar(vazio(), '123-1', agora);
    expect(ledger.reservas[0]).toEqual({ id: '123-1', fase: 'melhorias', centavos: 10, data: agora.toISOString() });
    expect(() => reservar(ledger, '123-1', agora)).toThrow(/já reservada/);
    expect(reservar(ledger, '123-2', agora).reservas).toHaveLength(2);
  });

  it('não reaproveita os US$6 em revisão e bloqueia cada teto inclusive após novas tentativas', () => {
    let ledger = vazio();
    for (let i = 1; i <= 60; i++) ledger = reservar(ledger, `${i}-1`, agora);
    expect(() => reservar(ledger, '61-1', agora)).toThrow(/esgotado/);
    const revisao = new Date('2026-10-29T03:00:00Z');
    for (let i = 61; i <= 90; i++) ledger = reservar(ledger, `${i}-1`, revisao);
    expect(() => reservar(ledger, '91-1', revisao)).toThrow(/esgotado/);
    let soRevisao = vazio();
    for (let i = 1; i <= 30; i++) soRevisao = reservar(soRevisao, `${i}-1`, revisao);
    expect(() => reservar(soRevisao, '31-1', revisao)).toThrow(/esgotado/);
  });

  it('recusa registros inválidos sem reiniciar o orçamento silenciosamente', () => {
    const base = reservar(vazio(), '1-1', agora);
    const entrada = base.reservas[0];
    for (const ledger of [null, {}, { version: 2, reservas: [] }, { version: 1, reservas: [], extra: true },
      { version: 1, reservas: [entrada, entrada] },
      ...[{ centavos: -10 }, { centavos: '10' }, { fase: 'revisao' }, { data: '2026-10-23T13:00:00.000Z' }, { id: 'abc' }]
        .map(mudanca => ({ version: 1, reservas: [{ ...entrada, ...mudanca }] }))]) {
      expect(() => reservar(ledger, '2-1', agora)).toThrow();
    }
  });
});

describe('entrada restrita e consulta única', () => {
  it('aceita código/documentação pertinente e bloqueia caminhos administrativos e credenciais', () => {
    for (const nome of ['src/telas/revisao.js', 'src/estilo.css', 'testes/exemplo.test.js', 'docs/FILA.md']) expect(caminhoPermitido(nome)).toBe(true);
    for (const nome of ['src/../segredo.js', 'src//exemplo.js', '/src/exemplo.js', 'src/dados/biblioteca.js', '.env', '.github/x.yml', 'src/token.js', 'docs/credentials.md']) expect(caminhoPermitido(nome)).toBe(false);
  });

  it('envia apenas arquivos rastreados regulares, nunca symlinks mesmo que substituam arquivo rastreado', () => {
    comRepositorio(raiz => {
      expect(preparar('Revisar.', 'src/exemplo.js', raiz).input).toContain('ficticio');
      writeFileSync(join(raiz, 'src/novo.js'), 'conteúdo');
      expect(() => preparar('Revisar.', 'src/novo.js', raiz)).toThrow(/rastreado/);
      rmSync(join(raiz, 'src/exemplo.js'));
      symlinkSync(join(raiz, 'src/novo.js'), join(raiz, 'src/exemplo.js'));
      expect(() => preparar('Revisar.', 'src/exemplo.js', raiz)).toThrow(/simbólicos/);
    });
  });

  it('nega segredos conhecidos, arquivos grandes e entrada UTF8 acima do limite', () => {
    comRepositorio(raiz => {
      writeFileSync(join(raiz, 'src/exemplo.js'), 'sk-' + 'x'.repeat(32));
      expect(() => preparar('Revisar.', 'src/exemplo.js', raiz)).toThrow(/credencial/);
      writeFileSync(join(raiz, 'src/exemplo.js'), 'a'.repeat(48001));
      expect(() => preparar('Revisar.', 'src/exemplo.js', raiz)).toThrow(/grande/);
    });
    expect(() => validarPacote({ ...pacote(), input: 'á'.repeat(24000) })).toThrow(/48000/);
    expect(() => validarPacote({ ...pacote(), tools: [{ type: 'web_search' }] })).toThrow(/configuração/);
    expect(() => validarPacote({ ...pacote(), max_output_tokens: 100000 })).toThrow(/configuração/);
    expect(() => validarPacote({ ...pacote(), model: 'outro-modelo' })).toThrow(/configuração/);
  });

  it('faz uma única chamada sem repetir erro HTTP ou revelar o corpo de erro', async () => {
    const json = vi.fn(() => ({ error: { message: 'segredo fictício' } }));
    const requisitar = vi.fn(async () => ({ ok: false, status: 429, json }));
    await expect(consultar(pacote(), 'ficticia', { requisitar, agora })).rejects.toThrow('HTTP 429');
    expect(requisitar).toHaveBeenCalledTimes(1);
    expect(json).not.toHaveBeenCalled();
    const falha = vi.fn(async () => { throw new Error('segredo fictício'); });
    await expect(consultar(pacote(), 'ficticia', { requisitar: falha, agora })).rejects.toThrow(/Falha de rede/);
    expect(falha).toHaveBeenCalledTimes(1);
  });

  it('bloqueia chamada vencida ou adulterada antes de acessar a API', async () => {
    const requisitar = vi.fn();
    await expect(consultar(pacote(), 'ficticia', { requisitar, agora: new Date('2026-11-01') })).rejects.toThrow(/prazo/);
    await expect(consultar({ ...pacote(), store: true }, 'ficticia', { requisitar, agora })).rejects.toThrow(/configuração/);
    await expect(consultar(pacote(), '', { requisitar, agora })).rejects.toThrow(/ausente/);
    expect(requisitar).not.toHaveBeenCalled();
  });

  it('registra uso e sinaliza saída incompleta sem alegar implementação', async () => {
    const requisitar = vi.fn(async () => ({ ok: true, json: async () => ({ status: 'incomplete', usage: { input_tokens: 1000, output_tokens: 8000 },
      output: [{ type: 'message', content: [{ type: 'output_text', text: 'Hipótese a conferir.' }] }] }) }));
    const resultado = await consultar(pacote(), 'ficticia', { requisitar, agora });
    expect(resultado.relatorio).toContain('incompleta');
    expect(resultado.relatorio).toContain('Hipótese a conferir.');
    expect(resultado.uso.custoEstimadoUSD).toBeCloseTo(0.03675);
    expect(requisitar.mock.calls[0][1].redirect).toBe('error');
    const corpo = JSON.parse(requisitar.mock.calls[0][1].body);
    expect(corpo.max_output_tokens).toBe(8000);
    expect(corpo.tools).toBeUndefined();
    expect(corpo.store).toBe(false);
  });
});
