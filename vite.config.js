import { defineConfig } from 'vite';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { configuracaoCatalogo } from './src/logica/catalogo.js';

/** A versão muda também quando só o conteúdo de um arquivo fixo ou do worker muda. */
export function versaoDoCache(arquivos) {
  const hash = createHash('sha256');
  for (const [nome, conteudo] of [...arquivos].sort(([a], [b]) => a.localeCompare(b))) {
    hash.update(nome).update('\0').update(conteudo).update('\0');
  }
  return hash.digest('hex').slice(0, 16);
}

// Gera o sw.js na pasta final com a lista de todos os arquivos do app,
// para o aplicativo abrir e gerar planilhas mesmo sem internet.
function serviceWorker() {
  return {
    name: 'pcm-service-worker',
    apply: 'build',
    generateBundle(_opcoes, pacote) {
      // Arquivos gerados pelo build + arquivos fixos da pasta public (manifesto e ícones)
      const publicos = readdirSync('public', { recursive: true })
        .map((f) => String(f).split(path.sep).join('/'))
        .filter((f) => statSync('public/' + f).isFile());
      const arquivos = [...Object.keys(pacote), ...publicos].filter((f) => !f.endsWith('.map')).sort();
      const worker = readFileSync('src/sw.js', 'utf8');
      const conteudos = arquivos.map((nome) => [nome, pacote[nome]
        ? (pacote[nome].type === 'chunk' ? pacote[nome].code : pacote[nome].source)
        : readFileSync(path.join('public', nome))]);
      const versao = versaoDoCache([...conteudos, ['src/sw.js', worker]]);
      const codigo = worker
        .replace('[/*ARQUIVOS*/]', JSON.stringify(arquivos.map((f) => './' + f)))
        .replace('/*VERSAO*/', versao);
      this.emitFile({ type: 'asset', fileName: 'sw.js', source: codigo });
    },
  };
}

// base relativa ('./') para o app funcionar em qualquer endereço,
// inclusive em https://<usuario>.github.io/pcm-direto/
export default defineConfig({
  base: './',
  plugins: [{
    name: 'pcm-configuracao-publica',
    configResolved(config) {
      const resultado = configuracaoCatalogo(config.env);
      if (resultado.erro) throw new Error(resultado.erro);
    },
  }, serviceWorker()],
  build: {
    // As bibliotecas de planilha e documento são grandes; o aviso padrão não ajuda aqui.
    chunkSizeWarningLimit: 2000,
  },
  test: {
    include: ['testes/**/*.test.js'],
  },
});
