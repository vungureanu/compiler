## About ##

The main purpose of this program is to reduce expressions of the pure, untyped lambda calculus to normal form using the normal-order evaluation strategy.  Also included are a lexer and parser which were used to construct this program; these can be used to parse other context-free grammars whose set of tokens is a regular language.

## How to Use ##

Assuming Python3 is installed, run the commands:

```git clone https://github.com/vungureanu/compiler.git
cd compiler
python3 untyped_lambda.py'''

You should see the prompt `>>`.  One can do three things at the prompt: enter `exit` to exit, enter a term of the (untyped) lambda calculus, and define an abbreviation for a term of the lambda calculus.  One can send an interrupt signal (e.g., by pressing Ctrl-C) to abort the current reduction.  Here is an example:

```>> 1

λf.λx.fx
Alias: 1
>> plus 1 1
((λm.λn.(mλn.λf.λx.f(nfx))n)λf.λx.fx)λf.λx.fx
(λn.((λf.λx.fx)λn.λf.λx.f(nfx))n)λf.λx.fx
((λf.λx.fx)λn.λf.λx.f(nfx))λf.λx.fx
(λx.(λn.λf.λx.f(nfx))x)λf.λx.fx
(λn.λf.λx.f(nfx))λf.λx.fx
λf.λx.f((λf.λx.fx)fx)
λf.λx.f((λx.fx)x)

λf.λx.f(fx)
Alias: 2
>> irreducible := (λx.x x) λx.x x
(λx.xx)λx.xx
Alias: irreducible
>> irreducible
Expression could not be reduced to normal form.
>> ternary true irreducible othervalue
Expression could not be reduced to normal form.
>> ternary false irreducible othervalue
(((λp.λa.λb.pab)λx.λy.y)((λx.xx)λx.xx))othervalue
((λa.λb.(λx.λy.y)ab)((λx.xx)λx.xx))othervalue
(λb.((λx.λy.y)((λx.xx)λx.xx))b)othervalue
((λx.λy.y)((λx.xx)λx.xx))othervalue
(λy.y)othervalue

othervalue
Alias: othervalue```

Lambda terms can be represented in the usual fashion, except the application of the term `F` to the term `A` must be written `F A` rather than `FA`.  The following abbreviations are pre-defined: the positive integers, `succ`, `pred`, `plus`, `mul`, `pow`, `true`, `false`, `and`, `or`, `not`, `ternary`, `iszero`, and `fix`.

This project contains two components.  The first is a compiler front-end consisting of a scanner, found in `finite_automata.py`, and a parser, found in `context_free_grammar.py`.  The function of the scanner is to transform a string into a sequence of `Token`s, which is then transformed by the parser into a `Parse_Node` which reflects its hierarchical structure.  The parser performs this transformation by means of the `Rule`s it is given.  The second component is an interpreter for the pure, untyped lambda calculus which uses the compiler front-end.

The file `finite_automata.py` contains classes which emulate both deterministic (`DFA`) and non-deterministic (`NFA`) finite automata, and allow for conversion between the two.  Each finite automaton recognizes a particular regular language; we shall call strings in that language _valid_.  The purpose of a finite automaton is to partition strings into `Token`s (via `scan`).  The string `s` is partitioned as follows: the first token is the longest valid substring starting with the first character of `s`; the n<sup>th</sup> token is the longest valid substring of `s` starting with the character after the last character of the n-1<sup>st</sup> token.  An automaton may be provided with an optional string `token_type`; the `token_type` property of tokens it produces will then be that string.  Given NFAs which recognize L and M, methods are provided for constructing an NFA which recognizes {lm | l in L and m in M}, {s | s in L or s in M}, {s<sub>1</sub>...s<sub>n</sub> | s<sub>i</sub> in L}, and {s | s not in L}.

To specify a context-free grammar, one provides a finite set of rules of the form V ⟶ T<sub>1</sub>...T<sub>n</sub>, where V is a variable and each T<sub>i</sub> is either a variable or a terminal.  This can be done by creating a member of class `Rule` whose property `lhs` is a `Token` representing V and whose property `rhs` is a list of `Token`s representing each of the T<sub>i</sub>.  Alternatively, one can use the class `Rule_Conversion` to transform strings into `Rule`s.  The first term represents the left-hand side of the rule and the remaining terms represent the right-hand side; bracketed terms represent variables, other terms represent terminals, `_` indicates a space, and terms are separated by spaces.  `Static_Rule`s represent rules whose proper application can be determined before the program is run, and `Dynamic_Rule`s represent other rules (e.g., rules whose right-hand sides may contain tokens corresponding to user-defined variables). 

The file `context_free_grammars.py` contains methods for converting a set of rules into Chomsky normal form.  This process involves several stages.  First, each non-solitary terminal appearing on the right-hand side of a rule is replaced with the variable V<sub>t</sub>, with the accompanying rule V<sub>t</sub> ⟶ t being added.  Next, rules of the form V ⟶ S<sub>1</sub>...S<sub>n</sub> are replaced with the rules V ⟶ S_1{S<sub>2</sub>...S</sub>n</sub>}, {S<sub>i</sub>...S<sub>n</sub>} ⟶ S<sub>i</sub>{S<sub>i+1</sub>...S<sub>n</sub>}, and {S<sub>n-1</sub>S<sub>n</sub>} ⟶ S<sub>n-1</sub>S<sub>n</sub>.  The property `expansion` indicates the user-defined tokens appearing in the right-hand side of a rule.  Then variables which can be reduced to the empty sequence are removed from the right-hand side of rules.  Finally, rules of the form A ⟶ B are removed, with the rule A ⟶ S<sub>1</sub>...S<sub>n</sub> being added for each rule of the form B ⟶ S<sub>1</sub>...S<sub>n</sub>.

A sequence of tokens T<sub>1</sub>...T<sub>n</sub> is parsed by building up a two-dimensional matrix M of parse trees: M<sub>ij</sub> contains possible parse trees for T<sub>i</sub>...T<sub>j</sub>.  For each rule of the form A ⟶ t, we should add the tree with root A and child t to M<sub>ii</sub>.  For each rule of the form S ⟶ TU, if M<sub>ij</sub> contains a parse tree with root T and U contains a parse tree with root U, then we should add a parse tree with root S and children T and U to M<sub>ik</sub>.  This is done by adding the appropriate parse trees to M<sub>i(i+l)</sub> for progressively larger values of l.  `Dynamic_Rule`s must be provided with a function `match_function` to determine whether they apply to a given right-hand side.  A `Parse_Node` represents a parse tree; it consists of a `Rule` together with the `Token` `lhs` to which it was applied to yield the list of `Parse_Node`s `rhs` (or a solitary `Token`).

Each `Rule` has a property `evaluation`, which is intended to be a function yielding values in a set V.  If a `Rule` represents a rule of the form A ⟶ t, then `evaluation` should accept `Token`s of type t and yield values in V.  If a `Rule` represents a rule of the form A ⟶ T<sub>1</sub>...T<sub>n</sub>, then `evaluation` should accept n values in V and yield a value in V.  The evaluation of a node in the parse tree is determined by the evaluations of its children.  Since `evaluation` is only defined for user-specified rules, there must be an "unwinding" procedure whereby any rules not specified by the user (namely, those introduced by the procedure to reduce the user-defined rules to Chomsky normal form) are removed from parse tree.  The partial unwinding of the `Parse_Node` `P` representing the derivation obtained via V ⟶ S<sub>1</sub>{S<sub>2</sub>...S</sub>n</sub>} is the list `[P.rhs[0]]` concatenated with the partial unwinding of `P.rhs[1]`.  The partial unwinding of other `Parse_Node` is just their `rhs`.  We then define the total unwinding of a `Parse_Node` in terms of the total unwindings of the `Parse_Node`s in its partial unwinding.

The file `untyped_lambda.py` is an implementation of the pure, untyped lambda calculus using the compiler front-end.  The `Static_Rule`s are chosen to ensure that terms can be unambiguously defined with a minimum of parentheses.  The `Dynamic_Rule`s are chosen so that the user can define variables and keywords.  The `evaluation` of a term consists of a tree of variables, applications, and lambda abstractions reflecting the structure of that term.  These are represented by members of the classes `Variable`, `Application`, and `Abstraction`.    It is reduced via the normal-order evaluation strategy.  If a substitution cannot be performed on a term due to variable conflicts, a fresh variable is introduced. 
