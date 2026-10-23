import { spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const imagem = 'postgres:17-alpine@sha256:eee6c6e1b0894fa4fe0075eb054af9fd1cf39a35321c2d4110626cfe506411fb';
const nome = `pcm-catalogo-teste-${randomUUID()}`;
const pasta = fileURLToPath(new URL('../supabase', import.meta.url));
const ambiente = { ...process.env };
// Use somente o daemon local; preserve a configuração e credenciais do cliente.
for (const chave of ['DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH']) {
  delete ambiente[chave];
}

function docker(argumentos, { verificar = true, mostrar = false, timeout = 30_000 } = {}) {
  const resultado = spawnSync('docker', ['--host=unix:///var/run/docker.sock', ...argumentos], {
    env: ambiente,
    encoding: 'utf8',
    stdio: mostrar ? 'inherit' : 'pipe',
    timeout,
  });
  if (verificar && (resultado.error || resultado.status !== 0)) {
    throw new Error(resultado.error?.message || resultado.stderr?.trim() || `Docker retornou ${resultado.status}.`);
  }
  return resultado;
}

let iniciado = false;
try {
  docker(['info', '--format', '{{.ServerVersion}}']);
  const disponivel = docker(['image', 'inspect', imagem], { verificar: false });
  if (disponivel.status !== 0) {
    throw new Error(`Imagem ausente. Baixe antes com: docker pull ${imagem}`);
  }
  docker(['run', '--detach', '--rm', '--pull=never', '--name', nome, '--network', 'none',
    '--env', 'POSTGRES_HOST_AUTH_METHOD=trust',
    '--mount', `type=bind,source=${pasta},target=/testes,readonly`, imagem]);
  iniciado = true;
  let pronto = false;
  for (let tentativa = 0; tentativa < 30; tentativa += 1) {
    if (docker(['exec', nome, 'pg_isready', '-h', '127.0.0.1', '-U', 'postgres'], { verificar: false, timeout: 5_000 }).status === 0) {
      pronto = true;
      break;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  if (!pronto) throw new Error('PostgreSQL descartável não ficou pronto no prazo.');
  docker(['exec', nome, 'psql', '-U', 'postgres', '-v', 'ON_ERROR_STOP=1',
    '-f', '/testes/testes/catalogo.sql'], { mostrar: true, timeout: 60_000 });
} catch (erro) {
  console.error(`Falha na verificação do catálogo: ${erro.message}`);
  process.exitCode = 1;
} finally {
  if (iniciado) {
    const limpeza = docker(['rm', '--force', '--volumes', nome], { verificar: false });
    if (limpeza.error || limpeza.status !== 0) {
      console.error(`Não foi possível remover o container descartável ${nome}.`);
      process.exitCode = 1;
    }
  }
}
