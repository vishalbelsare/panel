import { HTMLBox } from "@bokehjs/models/layouts/html_box";
import * as p from "@bokehjs/core/properties";
import { PanelHTMLBoxView } from "./layout";
export declare class TerminalView extends PanelHTMLBoxView {
    model: Terminal;
    term: any;
    fitAddon: any;
    webLinksAddon: any;
    container: HTMLDivElement;
    _rendered: boolean;
    connect_signals(): void;
    render(): void;
    getNewTerminal(): any;
    getNewWebLinksAddon(): any;
    handleOnData(value: string): void;
    write(): void;
    clear(): void;
    fit(): void;
    after_layout(): void;
    resize_layout(): void;
}
export declare namespace Terminal {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        options: p.Property<any>;
        output: p.Property<string>;
        input: p.Property<string>;
        _clears: p.Property<number>;
        _value_repeats: p.Property<number>;
    };
}
export interface Terminal extends Terminal.Attrs {
}
export declare class Terminal extends HTMLBox {
    properties: Terminal.Props;
    constructor(attrs?: Partial<Terminal.Attrs>);
    static __module__: string;
    static init_Terminal(): void;
}
