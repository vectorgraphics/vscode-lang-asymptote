import * as net from "net";
import * as vscode from "vscode";

import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  Executable,
  StreamInfo,
} from "vscode-languageclient/node";

let client: LanguageClient;

function getServerOptTCP(port: number): () => Promise<StreamInfo> {
  return function () {
    return new Promise((resolve, _reject) => {
      const sock = new net.Socket();
      sock.connect(port, "127.0.0.1", () =>
        resolve({ reader: sock, writer: sock }),
      );
    });
  };
}

function getServerOpt(
  cmd: string = "asy",
  additionalArgs: string[] = [],
): Executable {
  // default args ["/mnt/d/Data/Source/asymptote/asy", "-lsp", "-noV", "-dir", "/mnt/d/Source/asymptote/base"]
  const args = ["-lsp", "-noV"];
  args.push(...additionalArgs);
  return {
    command: cmd,
    args: args,
  };
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function activate(context: vscode.ExtensionContext) {
  const port = 10007;
  const clientOpt: LanguageClientOptions = {
    documentSelector: [{ language: "asymptote", scheme: "file" }],
    outputChannelName: "[asylsp] AsymptoteLsp",
  };

  const config: vscode.WorkspaceConfiguration =
    vscode.workspace.getConfiguration("asymptote");

  const asyCmd: string | undefined = config.get<string>("asyCmd");
  const additionalArgs: string[] | undefined =
    config.get<string[]>("additionalArgs");

  let serverOpt: ServerOptions;
  if (process.env.FORCE_ASY_TCP_MODE === "true") {
    console.log("Starting in TCP mode...");
    serverOpt = getServerOptTCP(10007);
  } else {
    serverOpt = getServerOpt(asyCmd, additionalArgs);
  }

  if (config.get("analysisEngine")) {
    client = new LanguageClient(`asylsp port (${port})`, serverOpt, clientOpt);
    client
      .start()
      .then(() => {
        console.log("asy lsp started");
      })
      .catch((err) => {
        console.error("asy lsp error: " + err.toString());
      });
  }
}

export function deactivate(): Promise<void> | undefined {
  console.log("extension stopped");
  if (!client) {
    return undefined;
  } else {
    return client.stop();
  }
}
