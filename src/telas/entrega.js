// Tela 4: Entrega — baixar a planilha .xlsx e o resumo .docx.
import { estado, dadosAtuais } from '../estado.js';
import { validarLista } from '../logica/validacao.js';
import { nomeArquivo } from '../logica/pacote.js';
import { gerarXlsx } from '../saida/xlsx.js';
import { montarDocx } from '../saida/docx.js';
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

    <section class="cartao">
      <h3>Seus modelos PCMD</h3>
      <p>Os novos documentos serão conectados aos modelos Excel e Word que você fornecer.
        A interface já guarda os cadastros e registros; os downloads acima continuam no formato anterior.</p>
      <ul>
        <li>PCMD-01 · Lista Mestra de Documentos — aguardando modelo.</li>
        <li>PCMD-02 · Ativos e Criticidade — aguardando modelo.</li>
        <li>PCMD-03 · Plano Mestre — aguardando modelo.</li>
        <li>PCMD-04 · Cronograma Anual — aguardando modelo.</li>
        <li>PCMD-05 · Ficha de Falha — aguardando modelo.</li>
        <li>PCMD-W1 e PCMD-W2 · Manuais — aguardando modelos.</li>
      </ul>
      <p>Guarde os cadastros e o histórico no <a href="#inicio">backup completo</a>.
        As exportações antigas ainda não incluem esses registros novos.</p>
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

  main.querySelector('#baixar-csv').addEventListener('click', () => {
    const linhas = estado.equipamentos.map((e) => ({ ...e, tipo: estado.biblioteca.tipos.find((t) => t.id === e.tipo)?.nome ?? e.tipo }));
    baixar('\uFEFF' + paraCsv(linhas), 'equipamentos.csv', 'text/csv;charset=utf-8');
  });
}
