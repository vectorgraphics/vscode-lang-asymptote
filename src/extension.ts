import * as net from 'net';
import * as vscode from 'vscode';

import {
    LanguageClient, LanguageClientOptions,
    ServerOptions, SocketTransport, TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient

function getServerOpt(port: number): ServerOptions {
    return function() {
        return new Promise((resolve, reject) => {
        const sock = new net.Socket();
        sock.connect(port, '127.0.0.1', () => resolve({reader: sock, writer: sock}));
        });
    }
}

export function activate(context: vscode.ExtensionContext) {
    const port = 10007;
    let clientOpt: LanguageClientOptions = {
        documentSelector: [{language: 'asymptote', scheme: 'file'}],
        outputChannelName: "[asylsp] AsymptoteLsp"
    };

    client = new LanguageClient(`asylsp port (${port})`, getServerOpt(port), clientOpt);
    context.subscriptions.push(client.start());
    console.log('asy lsp started');
}

export function deactivate() {
    console.log('extension stopped')
    if (!client) {
        return undefined;
    } else {
        return client.stop();
    }
}