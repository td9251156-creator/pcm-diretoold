<p align="center"><img src="public/icones/logo.svg" alt="PCM Direto" width="160"></p>

# PCM Direto

Gerador de PCM (Planejamento e Controle de Manutenção) aberto e em português.
Você informa a lista de equipamentos e recebe o plano de manutenção preventiva pronto,
com cronograma anual, em planilha (.xlsx) e documento (.docx).

- Roda 100% no navegador: sem servidor, sem login e sem banco de dados.
- Seus dados ficam só no seu computador ou celular (lista salva no próprio navegador).
- Funciona como aplicativo no PC e no celular (PWA instalável).
- Gratuito e de código aberto (licença MIT).

> **Aviso:** O material apoia a organização do PCM e não substitui a avaliação de profissional
> habilitado nem o texto oficial das normas. As periodicidades são base genérica e devem ser
> confirmadas com o manual do fabricante.

## Como usar

1. **Início:** abra o app. Um exemplo com dados fictícios já vem carregado para você ver o resultado.
2. **Equipamentos:** cadastre um a um, cole direto do Excel ou importe uma planilha (.xlsx) ou CSV.
   O app gera a TAG padronizada (setor + tipo + número) e aponta erros com sugestão de correção.
3. **Revisão:** confira as tarefas de cada equipamento e ajuste periodicidades.
   Tarefas de segurança só aceitam periodicidade igual ou mais frequente que a da biblioteca.
   Escolha a data de início do plano: o cronograma mostra o dia em que cada semana começa
   e a carga de horas por semana de cada especialidade.
   Informe as horas disponíveis por semana em cada especialidade: o cronograma respeita esse limite.
4. **Entrega:** baixe a planilha (.xlsx) e o resumo (.docx), ou imprima o cronograma em A4 deitado.

Extras: a tela **Biblioteca técnica** (link no Início) permite editar tarefas e criar tipos de equipamento
no próprio app, e o botão de tema no rodapé alterna entre claro, escuro e automático.

Ao importar uma biblioteca `.json`, o app confere o formato antes de substituir a biblioteca atual.
Se houver campos inválidos ou códigos repetidos, ele informa o problema e mantém a biblioteca em uso.

Se dados salvos estiverem danificados, o app avisa e oferece o download dos originais para recuperação.
Antes de substituir esses dados, guarda uma cópia local; se não houver espaço, mantém o original.

O **Checklist de execução**, acessível pelo Início ou pela Revisão, permite marcar a execução,
registrar a data e uma observação técnica sem dados pessoais. Guarda apenas a última marcação
de cada tarefa neste aparelho, com opção de baixar as marcações em JSON. Isso não muda a frequência
nem o cronograma do plano e não substitui um histórico completo de execução.

Em **Início → Seus dados**, baixe o **backup completo (.json)** para guardar ou levar a outro aparelho
a lista, a biblioteca, os ajustes, a capacidade, a data de início e as marcações de execução.
Para restaurar, selecione esse arquivo e confirme a substituição. Arquivos inválidos são recusados.
O app preserva o par anterior de biblioteca e lista se a gravação da restauração for interrompida.

Na tela **Equipamentos**, **Desfazer última remoção** recupera a última máquina removida nesta sessão,
incluindo seus ajustes e marcações. Essa opção não recupera dados após fechar a página ou começar uma lista nova.

Na impressão do cronograma, filtre por **setor** e **especialidade**. As horas impressas refletem
somente as tarefas visíveis, sem redistribuir semanas. Os alertas de capacidade do plano completo
continuam aparecendo; os arquivos da Entrega mantêm o plano completo.

A planilha tem as abas: Leia-me, Resumo, Equipamentos, Plano, Cronograma e Ficha de Falha.
Ela usa só funções clássicas (PROCV, ÍNDICE, CORRESP), sem macros, e abre em versões antigas do Excel.

### Formato para colar do Excel ou importar CSV

Colunas, nesta ordem, com ou sem linha de cabeçalho:

```
setor;tipo;descricao;fabricante;modelo
UTL;compressor_ar;Compressor da linha de ar;Fabricante Exemplo;CX-100
```

Tipos aceitos na biblioteca inicial: `motor_eletrico`, `compressor_ar`, `bomba_centrifuga`, `ponte_rolante`.
O separador pode ser ponto e vírgula, vírgula ou tabulação (o padrão ao copiar do Excel).

## Pacote PCMD em construção

Na tela **Entrega**, o botão **Pacote PCMD — Ativos e criticidade (.xlsx)** baixa o protótipo
PCMD-02 separado da planilha e do resumo atuais. Ele aproveita os ativos já cadastrados e oferece
cinco notas de criticidade para preencher no Excel. Notas vazias ou inválidas ficam **Pendente**.
Os limites iniciais A≥12 e B≥9 são sugestões editáveis; segurança com nota 3 determina classe A.
Confirme os critérios com o responsável antes de usar o resultado para decisões de manutenção.

Esta etapa contém Leia-me, Ativos e Criticidade, Listas e Cadastros mínimos. Os demais documentos,
o histórico completo e a importação da planilha serão acrescentados por etapas; o app ainda não
recebe de volta essas notas. Guarde o arquivo preenchido: gerar outro não recupera suas edições.
Compatibilidade pretendida: Excel 2010. Fórmulas levam cache inicial e recálculo ao abrir; consulte
o Leia-me e pressione F9 se necessário. A conferência manual nessa versão continua pendente.
Para revisar um exemplo fictício, rode `npm run gerar:prototipo-pcmd`: o XLSX e os valores
esperados ficam em `artifacts/pcmd/` e também no artefato `prototipo-pcmd-02` do Actions.
Com LibreOffice instalado, `npm run verificar:recalculo-pcmd` compara os resultados recalculados
com as regras JavaScript. Veja o [plano e as etapas](docs/PLANO-TEMPLATES.md).

## Como rodar no seu computador

Pré-requisito: [Node.js LTS](https://nodejs.org/) instalado.

```bash
npm install
npm run dev
```

Abra o endereço que aparecer no terminal (normalmente http://localhost:5173).

Outros comandos:

| Comando           | O que faz                                          |
|-------------------|----------------------------------------------------|
| `npm test`        | Roda os testes automáticos                         |
| `npm run lint`    | Verifica o código                                  |
| `npm run build`   | Gera a versão final na pasta `dist/`               |
| `npm run preview` | Abre a versão final localmente                     |

## Logo e ícones

O logo fica em [`public/icones/logo.svg`](public/icones/logo.svg). Os ícones do aplicativo
(`icone-192.png`, `icone-512.png` e `icone-maskable-512.png`) são imagens geradas a partir dele.
Para trocar o logo, substitua esses quatro arquivos mantendo os nomes.
As letras do logo usam a fonte DejaVu Sans Bold (licença livre do projeto DejaVu), convertidas em desenho
para aparecerem iguais em qualquer aparelho.

## Biblioteca técnica

As tarefas de manutenção ficam em um único arquivo: [`src/dados/biblioteca.json`](src/dados/biblioteca.json).
Veja [BIBLIOTECA.md](BIBLIOTECA.md) para entender o formato e o checklist de revisão.

## Documentos do projeto

[ROADMAP.md](ROADMAP.md) · [DECISOES.md](DECISOES.md) · [CONTRIBUTING.md](CONTRIBUTING.md) ·
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) · [SECURITY.md](SECURITY.md) · [LICENSE](LICENSE)

[Lista priorizada de melhorias](docs/MELHORIAS.md), com problemas encontrados e próximas rodadas.
[Histórico das revisões e melhorias](docs/REVISOES.md).

[Estratégia de evolução com agentes](docs/EVOLUCAO-CONTINUA.md) · [Fila de trabalho atual](docs/FILA.md).

## Sobre o autor

**Thiago Oliveira Lima** — Engenheiro de Produção com mais de 10 anos em manutenção industrial no setor automotivo,
com experiência em PCM, análise de falhas (8D, MASP, FMEA), auditorias ISO e indicadores de manutenção.
[linkedin.com/in/thiagooliveiralima94](https://linkedin.com/in/thiagooliveiralima94)

Parte do código deste projeto foi escrita com ajuda de IA e revisada pelo autor.

## Licença

[MIT](LICENSE) — Copyright (c) 2026 Thiago Oliveira Lima.
