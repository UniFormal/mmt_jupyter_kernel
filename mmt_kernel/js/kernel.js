define([
        'base/js/namespace',
        'base/js/events',
        'notebook/js/codecell',
        'codemirror/lib/codemirror',
        'require'
], function (Jupyter, events, codecell, CodeMirror, require) {
        "use strict";

        return {
                onload: function () {
                        "use strict";

                        function wordRegexp(words) {
                                return new RegExp("^((" + words.join(")|(") + "))\\b");
                        }

                        var commonKeywords = ["include"];
                        var commonBuiltins = ["prop"];
                        var commonDefiners = ["theory", "view"];
                        var commonKernelCommands = ["active computation", "eval"];
                        var commonVariables = [];
                        var objectDelimiter = '\u2758';
                        var declarationDelimiter = '\u2759'
                        var moduleDelimiter = '\u275A'
                        CodeMirror.registerHelper("hintWords", "mmt", commonKeywords.concat(commonBuiltins));

                        function top(state) {
                                return state.scopes[state.scopes.length - 1];
                        }

                        CodeMirror.defineMode("mmt", function (conf, parserConf) {
                                var ERRORCLASS = "error";

                                var delimiters = parserConf.delimiters || parserConf.singleDelimiters || /^[\(\)\[\]\{\}@,:`=;\.\\]/;
                                //               (Backwards-compatiblity with old, cumbersome config system)
                                var operators = [parserConf.singleOperators, parserConf.doubleOperators, parserConf.doubleDelimiters, parserConf.tripleDelimiters,
                                parserConf.operators || /^([-⋅≐+*/%\/&|^]=?|[<>=]+|\/\/=?|\*\*=?|!=|[~!@])/]
                                for (var i = 0; i < operators.length; i++) if (!operators[i]) operators.splice(i--, 1)

                                var hangingIndent = parserConf.hangingIndent || conf.indentUnit;

                                var myKeywords = commonKeywords, myBuiltins = commonBuiltins;
                                if (parserConf.extra_keywords != undefined)
                                        myKeywords = myKeywords.concat(parserConf.extra_keywords);

                                if (parserConf.extra_builtins != undefined)
                                        myBuiltins = myBuiltins.concat(parserConf.extra_builtins);

                                var py3 = !(parserConf.version && Number(parserConf.version) < 3)
                                if (py3) {
                                        // since http://legacy.python.org/dev/peps/pep-0465/ @ is also an operator
                                        var identifiers = parserConf.identifiers || /^[_A-Za-z\u00A1-\uFFFF][_A-Za-z0-9\u00A1-\uFFFF]*/;
                                        myKeywords = myKeywords.concat(["nonlocal", "False", "True", "None", "async", "await"]);
                                        myBuiltins = myBuiltins.concat(["ascii", "bytes", "exec", "print"]);
                                        var stringPrefixes = new RegExp("^(([rbuf]|(br)|(fr))?('{3}|\"{3}|['\"]))", "i");
                                } else {
                                        var identifiers = parserConf.identifiers || /^[_A-Za-z][_A-Za-z0-9]*/;
                                        myKeywords = myKeywords.concat(["exec", "print"]);
                                        myBuiltins = myBuiltins.concat(["apply", "basestring", "buffer", "cmp", "coerce", "execfile",
                                                "file", "intern", "long", "raw_input", "reduce", "reload",
                                                "unichr", "unicode", "xrange", "False", "True", "None"]);
                                        var stringPrefixes = new RegExp("^(([rubf]|(ur)|(br))?('{3}|\"{3}|['\"]))", "i");
                                }
                                var keywords = wordRegexp(myKeywords);
                                var builtins = wordRegexp(myBuiltins);
                                var kernelCommands = wordRegexp(commonKernelCommands)
                                var definers = wordRegexp(commonDefiners);

                                // tokenizers
                                function tokenBase(stream, state) {
                                        var sol = stream.sol() && state.lastToken != "\\"
                                        if (sol) state.indent = stream.indentation()
                                        // Handle scope changes
                                        if (sol && top(state).type == "py") {
                                                var scopeOffset = top(state).offset;
                                                if (stream.eatSpace()) {
                                                        var lineOffset = stream.indentation();
                                                        if (lineOffset > scopeOffset)
                                                                pushPyScope(state);
                                                        else if (lineOffset < scopeOffset && dedent(stream, state) && stream.peek() != "#")
                                                                state.errorToken = true;
                                                        return null;
                                                } else {
                                                        var style = tokenBaseInner(stream, state);
                                                        if (scopeOffset > 0 && dedent(stream, state))
                                                                style += " " + ERRORCLASS;
                                                        return style;
                                                }
                                        }
                                        return tokenBaseInner(stream, state);
                                }


                                function tokenComment(stream, state) {
                                        if (stream.match(/-}/)) {
                                                state.tokenize = tokenBase;
                                                return "comment";
                                        }
                                        stream.next();
                                        return "comment";
                                }


                                function tokenBaseInner(stream, state) {
                                        if (stream.eatSpace()) return null;

                                        // Handle Comments
                                        if (stream.match(/^\\T.*/)) return "comment";

                                        // // Handle multiline comments
                                        // if (stream.match(/{-/)) {
                                        //         state.tokenize = tokenComment
                                        //         return state.tokenize(stream, state);
                                        // }

                                        // Handle Number Literals
                                        if (stream.match(/^[0-9\.]/, false)) {
                                                var floatLiteral = false;
                                                // Floats
                                                if (stream.match(/^[\d_]*\.\d+(e[\+\-]?\d+)?/i)) { floatLiteral = true; }
                                                if (stream.match(/^[\d_]+\.\d*/)) { floatLiteral = true; }
                                                if (stream.match(/^\.\d+/)) { floatLiteral = true; }
                                                if (floatLiteral) {
                                                        // Float literals may be "imaginary"
                                                        stream.eat(/J/i);
                                                        return "number";
                                                }
                                                // Integers
                                                var intLiteral = false;
                                                // Hex
                                                if (stream.match(/^0x[0-9a-f_]+/i)) intLiteral = true;
                                                // Binary
                                                if (stream.match(/^0b[01_]+/i)) intLiteral = true;
                                                // Octal
                                                if (stream.match(/^0o[0-7_]+/i)) intLiteral = true;
                                                // Decimal
                                                if (stream.match(/^[1-9][\d_]*(e[\+\-]?[\d_]+)?/)) {
                                                        // Decimal literals may be "imaginary"
                                                        stream.eat(/J/i);
                                                        // TODO - Can you have imaginary longs?
                                                        intLiteral = true;
                                                }
                                                // Zero by itself with no other piece of number.
                                                if (stream.match(/^0(?![\dx])/i)) intLiteral = true;
                                                if (intLiteral) {
                                                        // Integer literals may be "long"
                                                        stream.eat(/L/i);
                                                        return "number";
                                                }
                                        }

                                        // Handle Strings
                                        if (stream.match(stringPrefixes)) {
                                                var isFmtString = stream.current().toLowerCase().indexOf('f') !== -1;
                                                if (!isFmtString) {
                                                        state.tokenize = tokenStringFactory(stream.current());
                                                        return state.tokenize(stream, state);
                                                } else {
                                                        state.tokenize = formatStringFactory(stream.current(), state.tokenize);
                                                        return state.tokenize(stream, state);
                                                }
                                        }

                                        for (var i = 0; i < operators.length; i++)
                                                if (stream.match(operators[i])) return "operator";

                                        if (stream.match(delimiters)) return "punctuation";

                                        if (stream.match(objectDelimiter)) return "objectDelimiter";
                                        if (stream.match(declarationDelimiter)) return "declarationDelimiter";
                                        if (stream.match(moduleDelimiter)) return "moduleDelimiter";

                                        if (state.lastToken == "." && stream.match(identifiers))
                                                return "property";

                                        if (stream.match(keywords) || stream.match(definers)) {
                                                return "keyword";
                                        }

                                        if (stream.match(builtins)) return "builtin";


                                        if (stream.match(kernelCommands)) return "atom";

                                        if (stream.match(identifiers,false)) {
                                                if (stream.sol() || commonDefiners.includes(state.lastToken)){
                                                        stream.match(identifiers)
                                                        return "def"
                                                }
                                                stream.match(identifiers)
                                                return "variable";
                                        }

                                        // Handle non-detected items
                                        stream.next();
                                        return ERRORCLASS;
                                }

                                function formatStringFactory(delimiter, tokenOuter) {
                                        while ("rubf".indexOf(delimiter.charAt(0).toLowerCase()) >= 0)
                                                delimiter = delimiter.substr(1);

                                        var singleline = delimiter.length == 1;
                                        var OUTCLASS = "string";

                                        function tokenFString(stream, state) {
                                                // inside f-str Expression
                                                if (stream.match(delimiter)) {
                                                        // expression ends pre-maturally, but very common in editing
                                                        // Could show error to remind users to close brace here
                                                        state.tokenize = tokenString
                                                        return OUTCLASS;
                                                } else if (stream.match('{')) {
                                                        // starting brace, if not eaten below
                                                        return "punctuation";
                                                } else if (stream.match('}')) {
                                                        // return to regular inside string state
                                                        state.tokenize = tokenString
                                                        return "punctuation";
                                                } else {
                                                        // use tokenBaseInner to parse the expression
                                                        return tokenBaseInner(stream, state);
                                                }
                                        }

                                        function tokenString(stream, state) {
                                                while (!stream.eol()) {
                                                        stream.eatWhile(/[^'"\{\}\\]/);
                                                        if (stream.eat("\\")) {
                                                                stream.next();
                                                                if (singleline && stream.eol())
                                                                        return OUTCLASS;
                                                        } else if (stream.match(delimiter)) {
                                                                state.tokenize = tokenOuter;
                                                                return OUTCLASS;
                                                        } else if (stream.match('{{')) {
                                                                // ignore {{ in f-str
                                                                return OUTCLASS;
                                                        } else if (stream.match('{', false)) {
                                                                // switch to nested mode
                                                                state.tokenize = tokenFString
                                                                if (stream.current()) {
                                                                        return OUTCLASS;
                                                                } else {
                                                                        // need to return something, so eat the starting {
                                                                        stream.next();
                                                                        return "punctuation";
                                                                }
                                                        } else if (stream.match('}}')) {
                                                                return OUTCLASS;
                                                        } else if (stream.match('}')) {
                                                                // single } in f-string is an error
                                                                return ERRORCLASS;
                                                        } else {
                                                                stream.eat(/['"]/);
                                                        }
                                                }
                                                if (singleline) {
                                                        if (parserConf.singleLineStringErrors)
                                                                return ERRORCLASS;
                                                        else
                                                                state.tokenize = tokenOuter;
                                                }
                                                return OUTCLASS;
                                        }
                                        tokenString.isString = true;
                                        return tokenString;
                                }

                                function tokenStringFactory(delimiter) {
                                        while ("rubf".indexOf(delimiter.charAt(0).toLowerCase()) >= 0)
                                                delimiter = delimiter.substr(1);

                                        var singleline = delimiter.length == 1;
                                        var OUTCLASS = "string";

                                        function tokenString(stream, state) {
                                                while (!stream.eol()) {
                                                        stream.eatWhile(/[^'"\\]/);
                                                        if (stream.eat("\\")) {
                                                                stream.next();
                                                                if (singleline && stream.eol())
                                                                        return OUTCLASS;
                                                        } else if (stream.match(delimiter)) {
                                                                state.tokenize = tokenBase;
                                                                return OUTCLASS;
                                                        } else {
                                                                stream.eat(/['"]/);
                                                        }
                                                }
                                                if (singleline) {
                                                        if (parserConf.singleLineStringErrors)
                                                                return ERRORCLASS;
                                                        else
                                                                state.tokenize = tokenBase;
                                                }
                                                return OUTCLASS;
                                        }
                                        tokenString.isString = true;
                                        return tokenString;
                                }

                                function pushPyScope(state) {
                                        while (top(state).type != "py") state.scopes.pop()
                                        state.scopes.push({
                                                offset: top(state).offset + conf.indentUnit,
                                                type: "py",
                                                align: null
                                        })
                                }

                                function pushBracketScope(stream, state, type) {
                                        var align = stream.match(/^([\s\[\{\(]|#.*)*$/, false) ? null : stream.column() + 1
                                        state.scopes.push({
                                                offset: state.indent + hangingIndent,
                                                type: type,
                                                align: align
                                        })
                                }

                                function dedent(stream, state) {
                                        var indented = stream.indentation();
                                        while (state.scopes.length > 1 && top(state).offset > indented) {
                                                if (top(state).type != "py") return true;
                                                state.scopes.pop();
                                        }
                                        return top(state).offset != indented;
                                }

                                function tokenLexer(stream, state) {
                                        if (stream.sol()) state.beginningOfLine = true;

                                        var style = state.tokenize(stream, state);
                                        var current = stream.current();

                                        // Handle decorators
                                        if (state.beginningOfLine && current == "@")
                                                return stream.match(identifiers, false) ? "meta" : py3 ? "operator" : ERRORCLASS;

                                        if (/\S/.test(current)) state.beginningOfLine = false;

                                        if ((style == "variable" || style == "builtin")
                                                && state.lastToken == "meta")
                                                style = "meta";

                                        // Handle scope changes.
                                        if (current == "pass" || current == "return")
                                                state.dedent += 1;

                                        if (current == "lambda") state.lambda = true;
                                        if (current == ":" && !state.lambda && top(state).type == "py")
                                                pushPyScope(state);

                                        if (current.length == 1 && !/string|comment/.test(style)) {
                                                var delimiter_index = "[({".indexOf(current);
                                                if (delimiter_index != -1)
                                                        pushBracketScope(stream, state, "])}".slice(delimiter_index, delimiter_index + 1));

                                                delimiter_index = "])}".indexOf(current);
                                                if (delimiter_index != -1) {
                                                        if (top(state).type == current) state.indent = state.scopes.pop().offset - hangingIndent
                                                        else return ERRORCLASS;
                                                }
                                        }
                                        if (state.dedent > 0 && stream.eol() && top(state).type == "py") {
                                                if (state.scopes.length > 1) state.scopes.pop();
                                                state.dedent -= 1;
                                        }

                                        return style;
                                }

                                var external = {
                                        startState: function (basecolumn) {
                                                return {
                                                        tokenize: tokenBase,
                                                        scopes: [{ offset: basecolumn || 0, type: "py", align: null }],
                                                        indent: basecolumn || 0,
                                                        lastToken: null,
                                                        variables: [],
                                                        lambda: false,
                                                        dedent: 0
                                                };
                                        },

                                        token: function (stream, state) {
                                                var addErr = state.errorToken;
                                                if (addErr) state.errorToken = false;
                                                var style = tokenLexer(stream, state);

                                                if (style && style != "comment")
                                                        state.lastToken = (style == "keyword" || style == "punctuation") ? stream.current() : style;
                                                if (style == "punctuation") style = null;

                                                if (stream.eol() && state.lambda)
                                                        state.lambda = false;
                                                return addErr ? style + " " + ERRORCLASS : style;
                                        },

                                        indent: function (state, textAfter) {
                                                if (state.tokenize != tokenBase)
                                                        return state.tokenize.isString ? CodeMirror.Pass : 0;

                                                var scope = top(state), closing = scope.type == textAfter.charAt(0)
                                                if (scope.align != null)
                                                        return scope.align - (closing ? 1 : 0)
                                                else
                                                        return scope.offset - (closing ? hangingIndent : 0)
                                        },

                                        electricInput: /^\s*[\}\]\)]$/,
                                        closeBrackets: { triples: "'\"" },
                                        lineComment: "\T",
                                        fold: "indent"
                                };
                                return external;
                        });

                        CodeMirror.defineMIME("text/mmt", "mmt");
                        console.info('MMT mode loaded');

                        var mmtStlye = document.createElement("link");
                        mmtStlye.type = "text/css";
                        mmtStlye.rel = "stylesheet";
                        mmtStlye.href = require.toUrl("./mmt.css");
                        mmtStlye.id = "mmt-css";
                        document.getElementsByTagName("head")[0].appendChild(mmtStlye);

                        codecell.CodeCell.options_default.cm_config.theme = "mmt";
                        var cells = Jupyter.notebook.get_cells().forEach(function (cell) {
                                if (cell instanceof codecell.CodeCell) {
                                        cell.code_mirror.setOption("theme", "mmt");
                                }
                        });

                        var words = function (str) { return str.split(" "); };


                }
        }


});