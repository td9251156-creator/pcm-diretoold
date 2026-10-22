// Tela 4: Entrega — baixar a planilha .xlsx e o resumo .docx.
import { estado, dadosAtuais } from '../estado.js';
import { validarLista } from '../logica/validacao.js';
import { nomeArquivo } from '../logica/pacote.js';
import { gerarXlsx } from '../saida/xlsx.js';
import { montarDocx } from '../saida/docx.js';
import { gerarPcmdXlsx } from '../saida/pcmd/xlsx.js';
import { esc, num, baixar, avisar } from '../ui.js';
import { paraCsv } from '../logica/entrada.js';

const XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

/** Desabilita o botão enquanto o arquivo é gerado. */
async function gerando(botao, tarefa) {
  const texto = botao.textContent;
  botao.disabled = true;
  botao.textContent = 'Gerando…';
  try {
    await tarefa();
  } catch (erro) {
    console.error(erro);
    avisar('Não foi possível gerar o arquivo. Tente de novo; se continuar, relate o problema no GitHub do projeto.');
  } finally {
    botao.disabled = false;
    botao.textContent = texto;
  }
}

export function telaEntrega(main) {
  const problemas = validarLista(estado.equipamentos, estado.biblioteca.tipos);
  const comErro = Object.keys(problemas).length;
  const vazio = !estado.equipamentos.length;
  const bloqueado = comErro || vazio;
  const dados = dadosAtuais();
  const r = dados.resumo;

  main.innerHTML = `
    <section class="cartao">
      <h2>Entrega</h2>
      ${vazio ? '<p class="erro"><strong>A lista está vazia.</strong> <a href="#equipamentos">Cadastre os equipamentos</a>.</p>' : ''}
      ${comErro ? `<p class="erro"><strong>${comErro} equipamento(s) com pendência.</strong>
        <a href="#equipamentos">Corrija na tela Equipamentos</a> para liberar os arquivos.</p>` : ''}
      ${bloqueado ? '' : `
        <ul class="numeros">
          <li><strong>${r.equipamentos}</strong> equipamentos</li>
          <li><strong>${r.tarefas}</strong> tarefas ativas (${r.tarefasSeguranca} de segurança)</li>
          <li><strong>${num(r.horasAno)} h</strong> previstas no ano</li>
        </ul>`}
      <div class="acoes">
        <button type="button" id="baixar-tudo" ${bloqueado ? 'disabled' : ''}>Baixar planilha e resumo</button>
        <button type="button" class="secundario" id="baixar-xlsx" ${bloqueado ? 'disabled' : ''}>Só a planilha (.xlsx)</button>
        <button type="button" class="secundario" id="baixar-docx" ${bloqueado ? 'disabled' : ''}>Só o resumo (.docx)</button>
        <a class="botao secundario" href="#impressao" ${bloqueado ? 'aria-disabled="true" tabindex="-1"' : ''}>Imprimir cronograma (A4)</a>
        <button type="button" class="secundario" id="baixar-csv" ${vazio ? 'disabled' : ''}>Baixar equipamentos (.csv)</button>
      </div>
    </section>

    <section class="cartao" aria-labelledby="titulo-pcmd">
      <h3 id="titulo-pcmd">Pacote PCMD</h3>
      <p>Primeira etapa: protótipo PCMD-02, com os ativos cadastrados e a matriz de criticidade.
        Preencha as cinco notas no Excel; campos vazios ou inválidos ficam Pendente.</p>
      <p>Os limites sugeridos A≥12 e B≥9 são editáveis. Segurança com nota 3 determina classe A.
        Confirme os critérios com o responsável antes de aplicar as orientações.</p>
      <p>O plano completo e os manuais PCMD virão nas próximas etapas. Esta planilha ainda não pode
        ser reimportada no app. Guarde o arquivo preenchido: gerar outro não recupera suas edições.</p>
      <button type="button" id="baixar-pcmd" ${bloqueado ? 'disabled' : ''}>Pacote PCMD — Ativos e criticidade (.xlsx)</button>
    </section>

    <section class="cartao">
      <h3>O que vem na planilha atual</h3>
      <ol>
        <li><strong>Leia-me:</strong> aviso, origem das tarefas e explicação de cada aba.</li>
        <li><strong>Resumo:</strong> números do plano, horas por especialidade e equipamentos por tipo.</li>
        <li><strong>Equipamentos:</strong> lista com TAG padronizada.</li>
        <li><strong>Plano:</strong> uma linha por tarefa, com periodicidade, especialidade, origem e versão.</li>
        <li><strong>Cronograma:</strong> semanas do ano (S1 a S52) de cada tarefa e horas por semana.</li>
        <li><strong>Ficha de Falha:</strong> modelo para começar o histórico.</li>
      </ol>
      <p>Só funções clássicas (PROCV, ÍNDICE, CORRESP, SOMASE, CONT.SE), sem macros: abre em versões antigas do Excel.</p>
      <p class="origem">${esc(estado.biblioteca.nome)}, versão ${esc(estado.biblioteca.versao)}. Ao terminar, guarde os arquivos:
      a lista fica salva só neste aparelho.</p>
    </section>
  `;

  // As bibliotecas de planilha e documento só são carregadas quando você pede o arquivo
  async function planilha() {
    const ExcelJS = (await import('exceljs')).default;
    const buffer = await gerarXlsx(dadosAtuais(), ExcelJS);
    baixar(new Blob([buffer], { type: XLSX_MIME }), nomeArquivo('xlsx'));
  }
  async function resumo() {
    const docx = await import('docx');
    baixar(await docx.Packer.toBlob(montarDocx(dadosAtuais(), docx)), nomeArquivo('docx'));
  }

  main.querySelector('#baixar-tudo').addEventListener('click', (e) => gerando(e.target, async () => {
    await planilha();
    await resumo();
    avisar('Planilha e resumo gerados. Confira a pasta de downloads.');
  }));
  main.querySelector('#baixar-xlsx').addEventListener('click', (e) => gerando(e.target, async () => {
    await planilha();
    avisar('Planilha gerada.');
  }));
  main.querySelector('#baixar-docx').addEventListener('click', (e) => gerando(e.target, async () => {
    await resumo();
    avisar('Resumo gerado.');
  }));

  main.querySelector('#baixar-pcmd').addEventListener('click', (e) => gerando(e.target, async () => {
    const ExcelJS = (await import('exceljs')).default;
    const buffer = await gerarPcmdXlsx(dadosAtuais(), ExcelJS);
    baixar(new Blob([buffer], { type: XLSX_MIME }), nomeArquivo('xlsx').replace('pcm-direto-', 'pcmd-02-'));
    avisar('Protótipo PCMD-02 gerado. Preencha as notas e guarde o arquivo; a reimportação ainda não está disponível.');
  }));

  main.querySelector('#baixar-csv').addEventListener('click', () => {
    const linhas = estado.equipamentos.map((e) => ({ ...e, tipo: estado.biblioteca.tipos.find((t) => t.id === e.tipo)?.nome ?? e.tipo }));
    baixar('\uFEFF' + paraCsv(linhas), 'equipamentos.csv', 'text/csv;charset=utf-8');
  });
}
