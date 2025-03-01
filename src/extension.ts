import * as net from 'net';
import * as vscode from 'vscode';

import {
    LanguageClient, LanguageClientOptions,
    ServerOptions, Executable
} from 'vscode-languageclient/node';

let client: LanguageClient

function getServerOptTCP(port: number): () => Promise<any> {
    return function() {
        return new Promise((resolve, reject) => {
        const sock = new net.Socket();
        sock.connect(port, '127.0.0.1', () => resolve({reader: sock, writer: sock}));
        });
    }
}

function getServerOpt(cmd: string="asy", additionalArgs: string[]=[], wsl: boolean=false): Executable {
    // default args ["/mnt/d/Data/Source/asymptote/asy", "-lsp", "-noV", "-dir", "/mnt/d/Source/asymptote/base", "-wsl"]
    let args = ['-lsp', '-noV']
    args.push(...additionalArgs);
    if (wsl) {
        let cmdArr = [cmd];
        cmdArr.push(...args);
        cmdArr.push('-wsl');
        return {
            command: "wsl",
            args: cmdArr
        };
    } else {
        return {
            command: cmd,
            args: args
        };
    }

}

export function activate(context: vscode.ExtensionContext) {
    const port = 10007;
    let clientOpt: LanguageClientOptions = {
        documentSelector: [{language: 'asymptote', scheme: 'file'}],
        outputChannelName: "[asylsp] AsymptoteLsp"
    };

    let config: vscode.WorkspaceConfiguration = vscode.workspace.getConfiguration('asymptote');

    let useWsl: boolean | undefined = false;
    if (process.platform === "win32") {
        console.log('detecting windows...')
        useWsl = config.get('WSLMode');
    }

    let asyCmd: string | undefined = config.get<string>('asyCmd');
    let additionalArgs: string[] | undefined = config.get<string[]>('additionalArgs');

    let serverOpt: ServerOptions;
    if (process.env.FORCE_ASY_TCP_MODE === "true") {
        console.log('Starting in TCP mode...')
        serverOpt = getServerOptTCP(10007)
    } else {
        serverOpt = getServerOpt(asyCmd, additionalArgs, useWsl);
    }

    if (config.get('analysisEngine')) {
        client = new LanguageClient(`asylsp port (${port})`, serverOpt, clientOpt);
        context.subscriptions.push(client.start());
        console.log('asy lsp started');
    }
}

export function deactivate(): Promise<void> | undefined {
    console.log('extension stopped')
    if (!client) {
        return undefined;
    } else {
        return client.stop();
    }
}