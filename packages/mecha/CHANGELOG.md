# Changelog

<!--next-version-placeholder-->

## v0.3.0 (2021-09-19)
### Feature
* Add dispatch rule priority ([`d2e18d3`](https://github.com/vberlier/mecha/commit/d2e18d3a32c3d0eeb5acaebe4a5423aaa1812424))
* Add serializer ([`914be79`](https://github.com/vberlier/mecha/commit/914be79967dc3cc478ac36aa4cdbb8a87b112e10))
* Tweak parser ([`3c3e81d`](https://github.com/vberlier/mecha/commit/3c3e81d3bc1c510c15333f7de4615d723b81df45))
* Parse subcommands ([`9797adf`](https://github.com/vberlier/mecha/commit/9797adf3bc26cde6da86f60d71e69e411dc76e9b))
* Add nbt path parser ([`a2e0a42`](https://github.com/vberlier/mecha/commit/a2e0a4221c73ef7d6fc9054785a6d5db1ed1c4d6))
* Handle selectors ([`47a83f0`](https://github.com/vberlier/mecha/commit/47a83f096c06eeab488baf55b96daaa8fe97a5b3))
* Add even more parsers ([`27bc814`](https://github.com/vberlier/mecha/commit/27bc814cc3d0d6d8934b4b380ddb4f52f4875843))
* Implement more parsers ([`506f5bd`](https://github.com/vberlier/mecha/commit/506f5bdd43f8262dfb75bec4834d1531da078f61))
* Add item parser ([`4419381`](https://github.com/vberlier/mecha/commit/44193813977169b4929320b17ab46d48240261bf))
* Parse nbt ([`5689dbc`](https://github.com/vberlier/mecha/commit/5689dbc254e878625911f9329a9448149026ba6f))
* Parse block and resource location ([`4a12917`](https://github.com/vberlier/mecha/commit/4a12917e2329ac974468ee4a6dc5825093ea02dd))
* Show empty children in ast dump ([`8eede2e`](https://github.com/vberlier/mecha/commit/8eede2ee5026289e8a5e94700dd5ca3a78c73419))
* Add json parsing ([`2aaea5c`](https://github.com/vberlier/mecha/commit/2aaea5c1a51a5c55391a66dbac3cad98bab17ccc))
* Add a bunch of parsers ([`31f512c`](https://github.com/vberlier/mecha/commit/31f512cb8058193981e3ba24e3732a2bd87ccd6d))

### Fix
* Differentiate tags from comments in multiline mode ([`222bc64`](https://github.com/vberlier/mecha/commit/222bc642b87afb3296ce2bf243dc022411dd8cb1))
* Properly handle multiline for say command ([`8d9e7bb`](https://github.com/vberlier/mecha/commit/8d9e7bb1e333b43e12a44097d157ac23c3b74a76))
* Workaround for distinguishing comments from tags ([`f684e8c`](https://github.com/vberlier/mecha/commit/f684e8c3b75cb0a03669afaf0e8da8b0adc5a8fb))
* Allow empty comments ([`02ddce6`](https://github.com/vberlier/mecha/commit/02ddce627754769b362f3d38724eaa1bb5edf95f))
* Make it possible to provide the multiline option upon instantiation ([`65d4d5d`](https://github.com/vberlier/mecha/commit/65d4d5d06d994b1ef4945355624fe5723e199085))
* Handle the case where eof has already been consumed ([`41e2175`](https://github.com/vberlier/mecha/commit/41e2175292e0e7c7c8cb3b4237e50a2f88bc931f))
* Communicate rule return value to the parent ([`cd18591`](https://github.com/vberlier/mecha/commit/cd18591f6ce4805321198bcf5fca47449287f50b))
* Only avoid quotes when the regex matches the entire string ([`8adbd18`](https://github.com/vberlier/mecha/commit/8adbd18be3646db2eba0df9a9cf9a6e612cb33c3))
* Separate AstValue into different nodes ([`35f1719`](https://github.com/vberlier/mecha/commit/35f1719c8a0d3c6d4cf85272c110eaf01d977385))
* Detect eof to avoid requiring a final newline ([`1a0fb3c`](https://github.com/vberlier/mecha/commit/1a0fb3c514dfe36cce45588b2e29bca7b427b186))
* Pyright thinks nbtlib types are unknown ([`f93bf51`](https://github.com/vberlier/mecha/commit/f93bf51336bf75f7fda4ad5e965c0b2578ca9d39))
* Handle nbt arrays and add more examples ([`be0eb3a`](https://github.com/vberlier/mecha/commit/be0eb3a62e4db031ba0a8fafe11992f06ab67cf6))
* Handle particle and add more examples ([`19e267d`](https://github.com/vberlier/mecha/commit/19e267d15798ef037184344f3cede3e99b8e9d8c))
* Handle a few selector edge cases and add more tests ([`66dad49`](https://github.com/vberlier/mecha/commit/66dad49f01cfdd34a0bd3f866036eb416b7532e6))
* Tweak selector constraints and add more tests ([`0c938af`](https://github.com/vberlier/mecha/commit/0c938afad40665266fe1212a2284da3d6f894c42))
* Properly validate swizzle ([`e7b8165`](https://github.com/vberlier/mecha/commit/e7b81656af4b095366ddd640f796e7bb4533b41f))
* Automatically redirect when leaf isn't executable ([`b4ba807`](https://github.com/vberlier/mecha/commit/b4ba80780ea624bd4a6456483e65ea5af2299b29))
* Parse uuids into UUID objects ([`08d7f80`](https://github.com/vberlier/mecha/commit/08d7f803b7dfd32c76fa2a86afd6ba0a3916bfcf))

## v0.2.0 (2021-07-24)
### Feature
* Add initial parser implementation ([`117d76d`](https://github.com/vberlier/mecha/commit/117d76d807b5a27e8b83a9cebd63c0d8ec70d8d4))

## v0.1.0 (2021-06-12)
### Feature
* Start working on a parser ([`739335c`](https://github.com/vberlier/mecha/commit/739335c4d2f1d09136291e03c2324491eb69279b))

## v0.0.1 (2021-01-27)
### Fix
* Trigger automatic release ([`bd9e578`](https://github.com/vberlier/mecha/commit/bd9e578e353faa958514625761bb28e43ca6694c))
