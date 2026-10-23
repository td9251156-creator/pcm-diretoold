<p align="center"><img src="public/icones/logo.svg" alt="PCM Direto" width="160"></p>

# PCM Direto

Gerador de PCM (Planejamento e Controle de Manutenção) aberto e em português.
Você informa a lista de equipamentos e recebe o plano de manutenção preventiva pronto,
com cronograma anual, em planilha (.xlsx) e documento (.docx).

- Gestão local no navegador, com catálogo colaborativo online opcional pelo Supabase.
- Inventário e histórico ficam no aparelho; apenas contribuições explícitas vão ao catálogo.
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

O **Checklist de execução**, acessível pelo menu Execuções, registra cada realização com data,
observação e responsável. O histórico pode ser baixado em JSON; cancelamentos preservam o registro.
Escolha uma ocorrência prevista para contar no realizado. Marcações antigas são preservadas como
legado sem vínculo, sem multiplicar execuções. Registrar uma realização não muda as frequências.

Em **Início → Seus dados**, baixe o **backup completo (.json)** para guardar ou levar a outro aparelho
a lista, a biblioteca, os ajustes, a capacidade, a data de início, os cadastros, a criticidade,
o histórico completo e as falhas. Backups antigos da versão 1 continuam aceitos; os novos usam versão 2.
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

## Interface de gestão

- **Cadastros:** organização/setores, pessoas/funções, consulta das frequências e tipos, metas e requisitos.
- **Criticidade:** cinco notas por ativo, limites A/B editáveis, sem alterar tarefas de segurança.
- **Plano Mestre:** tarefas ativas e responsáveis, com busca e próximas ocorrências do cronograma atual.
- **Mensal:** janeiro a dezembro do ano consultado; horas, previsto e realizado com vínculo explícito.
- **Falhas:** registro e correção de sintoma, causa provável, ação, parada e responsável.

Pessoas podem ser editadas e inativadas. Preencha e salve cada formulário; os rascunhos dos demais
formulários de Cadastros são preservados ao salvar outro cadastro na mesma tela. Remover um ativo
não apaga os registros anteriores: eles ficam identificados como fora da lista atual.
Metas não definidas permanecem vazias. O app não calcula MTBF, MTTR ou disponibilidade sem regras
técnicas aprovadas. Referências começam não verificadas; nenhuma conformidade é certificada.

**Você fornecerá os modelos Excel e Word.** Esta entrega não cria templates PCMD. A Entrega informa
quais modelos ainda faltam, mantendo a planilha e o resumo anteriores. Esses arquivos antigos ainda
não contêm os cadastros novos; use o backup completo para guardar tudo. O
[guia para criar seus modelos](docs/INTERFACE-E-MODELOS.md) descreve campos e vínculos de cada documento.

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


## Catálogo colaborativo: direção autorizada em 22/10/2026

A restrição anterior de ausência de login/banco é substituída somente para o catálogo público
de modelos reutilizáveis. A gestão da fábrica continua local e não é sincronizada. Contribuições
explícitas usam Supabase Auth/PostgreSQL, com revisão antes da publicação. Código preparado
não significa serviço online ativado. Consulte [configuração do catálogo](docs/CATALOGO-COLABORATIVO.md) e [ativação dos benefícios](docs/ATIVACAO-STUDENT.md).
