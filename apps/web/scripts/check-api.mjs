import { execFile } from "node:child_process"
import { mkdtemp, readFile, rm } from "node:fs/promises"
import { tmpdir } from "node:os"
import { join, resolve } from "node:path"
import { promisify } from "node:util"

const run = promisify(execFile)
const temporary = await mkdtemp(join(tmpdir(), "asl-openapi-"))
try {
  const generated = join(temporary, "api.ts")
  const binary = resolve("node_modules/.bin/openapi-typescript")
  await run(binary, ["../../services/engine/openapi.json", "-o", generated])
  const committed = await readFile("src/generated/api.ts", "utf8")
  const current = await readFile(generated, "utf8")
  if (committed !== current) {
    throw new Error("Generated TypeScript API types are out of date")
  }
  process.stdout.write("Generated TypeScript API types match\n")
} finally {
  await rm(temporary, { recursive: true, force: true })
}
