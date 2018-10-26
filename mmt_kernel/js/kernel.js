// Add rulers to codecells
define([
        'base/js/namespace',
        'base/js/events',
        'notebook/js/codecell',
        'codemirror/lib/codemirror',
        'require'
    ], function(Jupyter, events, codecell, CodeMirror,require) {
        "use strict";

        return {onload: function(){
                CodeMirror.defineMode("mmt", function() {
                function words(array) {
                        var keys = {};
                        for (var i = 0; i < array.length; ++i) {
                                keys[array[i]] = true;
                        }
                        return keys;
                }
                
                var keywords = words(["theory", "view", "include", "import", "namespace"]);
                var builtins = words(["MitM", "smglom", "Foundation"]);
        
                var dataTypes =  words(["QE Velocity"]);
                var isURLSeparatorChar = /[\/\?\:]/;
                var isOperatorChar = /[=|+-\/]/;
                var objectDelimiter = '\u2758';
                var declarationDelimiter = '\u2759'
                var moduleDelimiter = '\u275A'
                var isDelimiterChar = /[\u2758\u2759\u275A]/;
        
                function tokenBase(stream, state) {
        
                        var ch = stream.next();
                        var next = stream.peek();
                        if (ch == "/" && next == "/") {
                                stream.skipToEnd();
                                return "comment";
                        }
                        if (ch == '"' || ch == "'") {
                                state.tokenize = tokenString(ch);
                                return state.tokenize(stream, state);
                        }
                        if (/[\[\]\(\),]/.test(ch)) {
                                return "bracket";
                        }
                        if (/\d/.test(ch)) {
                                stream.eatWhile(/[\d\.]/);
                                if(isOperatorChar.test(stream.peek()) || isDelimiterChar.test(stream.peek()) || stream.peek() == " " || stream.peek() == null){
                                        return "number";
                                }
                
                        }
                        if (isURLSeparatorChar.test(ch)) {
                                stream.eatWhile(isURLSeparatorChar);
                                return "separator";
                        }
                        if (isOperatorChar.test(ch)) {
                                stream.eatWhile(isOperatorChar);
                                return "operator";
                        }
                        if (isDelimiterChar.test(ch)) {
                                if(ch == objectDelimiter){
                                        return 'objectDelimiter';
                                }
                                if(ch == declarationDelimiter){
                                        return 'declarationDelimiter';
                                }
                                if(ch == moduleDelimiter){
                                        return 'moduleDelimiter';
                                }
                        }
                        stream.eatWhile(/[\w_]/);
                        var word = stream.current();
        
                        if (keywords.hasOwnProperty(word)){
                                if(word == "theory" || word == "view"){
                                        return 'theory';
                                }
                                return 'keyword';
                        }
                        if (builtins.hasOwnProperty(word) || dataTypes.hasOwnProperty(word)) {
                                return 'builtin';
                        }
                        return 'variable';
                }
        
                function tokenString(quote) {
                        return function(stream, state) {
                                var escaped = false, next, end = false;
                                while ((next = stream.next()) != null) {
                                        if (next == quote && !escaped) {
                                                end = true;
                                                break;
                                        }
                                        escaped = !escaped && next == "\\";
                                }
                                if (end || !escaped){
                                        state.tokenize = null;
                                } 
                                return "string";
                        };
                }
        
                // Interface

                return {
                startState: function() {
                        return {tokenize: null};
                },

                token: function(stream, state) {
                        if (stream.eatSpace()) return null;
                                var style = (state.tokenize || tokenBase)(stream, state);
                                if (style == "comment" || style == "meta") return style;
                                return style;
                        }
                };
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
        }}
    

    });