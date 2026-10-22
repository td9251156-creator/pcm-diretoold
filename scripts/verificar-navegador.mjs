// Verificação de ponta a ponta exigida pela CI, com ferramenta isolada do aplicativo.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import ExcelJS from 'exceljs';
import { AVISO } from '../src/logica/pacote.js';
import { iniciarServidor, aguardarOffline, executarComRecursos } from './navegador.mjs';

const ferramenta = process.env.PCM_PLAYWRIGHT || new URL('../ferramentas/navegador/node_modules/playwright/index.mjs', import.meta.url).href;
const { chromium } = await import(ferramenta);
const raiz = fileURLToPath(new URL('../', import.meta.url));
await executarComRecursos({
  criarServidor: () => iniciarServidor({ raiz }),
  criarNavegador: () => chromium.launch({
    executablePath: process.env.PCM_CHROMIUM || undefined,
    args: process.env.PCM_SEM_SANDBOX === '1' ? ['--no-sandbox'] : [],
    timeout: 20000,
  }),
  executar: async ({ navegador: browser }) => {
    const contexto = await browser.newContext({ viewport: { width: 390, height: 844 }, acceptDownloads: true });
    contexto.setDefaultTimeout(15000);
    contexto.setDefaultNavigationTimeout(30000);
    const page = await contexto.newPage();
    const erros = [];
    page.on('pageerror', (e) => erros.push(e.message));
    await page.goto('http://127.0.0.1:4175/');
    await page.getByRole('heading', { name: 'Plano de manutenção preventiva a partir da sua lista de equipamentos' }).waitFor();
    await page.getByRole('link', { name: '2. Equipamentos' }).focus();
    await page.keyboard.press('Enter');
    await page.waitForURL('**/#equipamentos');
    await page.waitForFunction(() => document.activeElement?.id === 'conteudo');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'conteudo');
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'A página excedeu a largura do celular');
    await page.locator('.pular').focus();
    await page.keyboard.press('Enter');
    assert.ok(page.url().endsWith('#equipamentos'), 'Pular para conteúdo não deve trocar de tela');
    await page.goto('http://127.0.0.1:4175/#revisao');
    const capacidade = page.locator('.capacidade').first();
    const aguardarRedesenho = () => page.evaluate(() => new Promise((resolve) =>
      requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await capacidade.waitFor();
    const idCapacidade = await capacidade.getAttribute('id');
    const idProximaCapacidade = await page.locator('.capacidade').nth(1).getAttribute('id');
    await capacidade.focus();
    for (const [tecla, valor] of [['ArrowUp', 0.5], ['ArrowUp', 1], ['ArrowDown', 0.5]]) {
      await capacidade.press(tecla);
      await aguardarRedesenho();
      await page.waitForFunction((id) => document.activeElement?.id === id, idCapacidade);
      assert.equal(Number(await capacidade.inputValue()), valor);
    }
    await capacidade.fill('2');
    await capacidade.press('Tab');
    await aguardarRedesenho();
    await page.waitForFunction((id) => document.activeElement?.id === id, idProximaCapacidade);
    await page.reload();
    await capacidade.waitFor();
    assert.equal(Number(await capacidade.inputValue()), 2);
    await capacidade.fill('');
    await capacidade.press('Tab');
    await aguardarRedesenho();
    await page.waitForFunction((id) => document.activeElement?.id === id, idProximaCapacidade);
    await page.goto('http://127.0.0.1:4175/#biblioteca');
    await page.locator('#importar-json').setInputFiles({ name: 'invalido.json', mimeType: 'application/json', buffer: Buffer.from('null') });
    await page.waitForFunction(() => document.querySelector('#mensagens').textContent.includes('Biblioteca não importada'));
    assert.equal(await page.locator('#tipos > details').count(), 4);
    await page.goto('http://127.0.0.1:4175/#execucao');
    await page.locator('#checklists details > summary').first().click();
    const tarefa = page.locator('#checklists form').first();
    await tarefa.locator('[name="concluida"]').check();
    await tarefa.locator('[name="observacao"]').fill('Conferência fictícia do roteiro de teste');
    await tarefa.getByRole('button').click();
    await page.waitForFunction(() => Object.keys(JSON.parse(localStorage.getItem('pcm-direto:rascunho:v1')).execucoes).length === 1);
    await page.reload();
    await page.locator('#checklists details > summary').first().click();
    assert.equal(await page.locator('#checklists form [name="concluida"]').first().isChecked(), true);
    await page.getByRole('link', { name: '1. Início' }).click();
    const [backup] = await Promise.all([page.waitForEvent('download'), page.locator('#baixar-backup').click()]);
    const bytesBackup = await readFile(await backup.path());
    page.on('dialog', (d) => d.accept());
    await page.locator('#em-branco').click();
    await page.getByRole('link', { name: '4. Entrega' }).click();
    assert.equal(await page.locator('#baixar-pcmd').isDisabled(), true, 'Lista vazia deve bloquear PCMD');
    await page.getByRole('link', { name: '1. Início' }).click();
    await page.locator('#restaurar-backup').setInputFiles({ name: 'backup.json', mimeType: 'application/json', buffer: bytesBackup });
    await page.waitForFunction(() => document.querySelector('#mensagens').textContent.includes('Backup restaurado'));
    assert.equal(await page.evaluate(() => Object.keys(JSON.parse(localStorage.getItem('pcm-direto:rascunho:v1')).execucoes).length), 1);
    await page.getByRole('link', { name: '2. Equipamentos' }).click();
    await page.locator('.equip').first().waitFor();
    const quantidade = await page.locator('.equip').count();
    await page.locator('.equip > summary').first().click();
    await page.locator('.equip .remover').first().click();
    await page.waitForFunction((q) => document.querySelectorAll('.equip').length === q, quantidade - 1);
    assert.equal(await page.locator('.equip').count(), quantidade - 1);
    await page.locator('#desfazer-remocao').click();
    await page.waitForFunction((q) => document.querySelectorAll('.equip').length === q, quantidade);
    assert.equal(await page.locator('.equip').count(), quantidade);
    // O pacote novo segue a mesma validação das exportações existentes.
    const descricao = page.locator('.equip [data-campo="descricao"]').first();
    const textoOriginal = await descricao.inputValue();
    await descricao.fill('');
    await page.getByRole('link', { name: '4. Entrega' }).click();
    assert.equal(await page.locator('#baixar-pcmd').isDisabled(), true, 'Pendência em ativo deve bloquear PCMD');
    await page.getByRole('link', { name: '2. Equipamentos' }).click();
    await page.locator('.equip [data-campo="descricao"]').first().fill(textoOriginal);
    await page.goto('http://127.0.0.1:4175/#impressao');
    await page.locator('#filtro-setor').selectOption('PRD');
    await page.locator('#filtro-especialidade').selectOption('Elétrica');
    assert.ok((await page.locator('#folha-cronograma tbody .tag').allTextContents()).every((tag) => tag.startsWith('PRD-')));
    assert.ok((await page.locator('#folha-cronograma tbody .tag').count()) > 0);
    assert.ok((await page.locator('#folha-cronograma').innerText()).includes('Filtros: PRD · Elétrica'));
    await page.goto('http://127.0.0.1:4175/#execucao');
    await aguardarOffline(page);
    await contexto.setOffline(true);
    await page.reload();
    await page.getByRole('heading', { name: 'Checklist de execução', exact: true }).waitFor();
    await page.getByRole('link', { name: '4. Entrega' }).click();
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Entrega deve caber no celular');
    const salvoAntesDoDownload = await page.evaluate(() => localStorage.getItem('pcm-direto:rascunho:v1'));
    for (const [botao, extensao] of [['#baixar-xlsx', '.xlsx'], ['#baixar-docx', '.docx'], ['#baixar-pcmd', '.xlsx']]) {
      if (botao === '#baixar-pcmd') await page.locator(botao).focus();
      const [arquivo] = await Promise.all([page.waitForEvent('download'), botao === '#baixar-pcmd' ? page.keyboard.press('Enter') : page.locator(botao).click()]);
      assert.ok(arquivo.suggestedFilename().endsWith(extensao));
      const bytes = await readFile(await arquivo.path());
      assert.ok(bytes.length > 5000);
      assert.equal(bytes.subarray(0, 2).toString(), 'PK');
      if (botao === '#baixar-pcmd') {
        assert.ok(arquivo.suggestedFilename().startsWith('pcmd-02-'));
        const wb = new ExcelJS.Workbook();
        await wb.xlsx.load(bytes);
        assert.deepEqual(wb.worksheets.map((a) => a.name), ['Leia-me', 'PCMD-02 Ativos e Criticidade', 'Listas', 'Cadastros']);
        for (const aba of wb.worksheets) {
          assert.ok(aba.headerFooter.oddFooter.includes(AVISO));
          assert.ok(aba.headerFooter.oddFooter.includes('Origem:'));
        }
        const valores = [];
        wb.getWorksheet('PCMD-02 Ativos e Criticidade').eachRow((r) => r.eachCell((c) => { if (c.formula) valores.push(c.result); }));
        assert.ok(valores.includes('Pendente'), 'Notas não informadas devem continuar pendentes');
      }
    }
    assert.equal(await page.evaluate(() => localStorage.getItem('pcm-direto:rascunho:v1')), salvoAntesDoDownload, 'Downloads não devem alterar rascunho');
    await contexto.setOffline(false);
    await page.goto('http://127.0.0.1:4175/#revisao');
    await page.evaluate(() => { Storage.prototype.setItem = () => { throw new Error('Falha simulada de armazenamento'); }; });
    await page.locator('.capacidade').first().fill('0.5');
    await page.locator('.capacidade').first().press('Tab');
    await page.locator('#aviso-armazenamento').waitFor({ state: 'visible' });
    await page.reload();
    await page.evaluate(() => localStorage.setItem('pcm-direto:rascunho:v1', '{'));
    await page.reload();
    await page.getByRole('button', { name: 'Baixar dados originais para recuperação' }).waitFor();
    assert.equal(await page.evaluate(() => localStorage.getItem('pcm-direto:rascunho:v1')), '{');
    assert.deepEqual(erros, []);
    console.log('Aprovado: celular, teclado, importação, checklist, backup/restauração, desfazer remoção, filtros, falha de gravação, recuperação, abertura offline e XLSX/DOCX/PCMD offline.');
  },
});
