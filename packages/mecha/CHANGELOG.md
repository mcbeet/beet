# Changelog

<!--next-version-placeholder-->

## v0.5.7 (2021-10-09)
### Fix
* Add logging for ast cache ([`c1bd76b`](https://github.com/mcbeet/mecha/commit/c1bd76beaa3262ec9b17d95267a050aa7aa16b1f))

## v0.5.6 (2021-10-09)
### Fix
* Fast path to avoid traversing ast when there are no rules ([`72322af`](https://github.com/mcbeet/mecha/commit/72322af610b725ec28cd6322cb8a5220beb1b7ae))
* Add ast cache ([`7ae025a`](https://github.com/mcbeet/mecha/commit/7ae025a635196d9abc0780ab5b8a3d8923a64c35))

## v0.5.5 (2021-10-09)
### Fix
* Handle more version formats in config ([`117bda1`](https://github.com/mcbeet/mecha/commit/117bda1f3a9c0617e7279f59777a7808c37e7fd4))

## v0.5.4 (2021-10-09)
### Fix
* Remove unnecessary args in serializer ([`cf041d6`](https://github.com/mcbeet/mecha/commit/cf041d6412cb63e79f8af5d89ec05c22f077576b))
* Add 1.18 command tree and handle player names and objectives with no length restriction ([`f1ffaa5`](https://github.com/mcbeet/mecha/commit/f1ffaa576d216d039d779179c22f5b5ce0f46678))

## v0.5.3 (2021-10-09)
### Fix
* Handle shortened UUID ([`8c2659b`](https://github.com/mcbeet/mecha/commit/8c2659b53f510b37f2fcb6274c87cf22c2e80af1))

## v0.5.2 (2021-10-09)
### Fix
* Don't log messages directly to avoid wrong percent formatting ([`abe1f99`](https://github.com/mcbeet/mecha/commit/abe1f99f8fc0765c10dcdee8d35bba29cdfac39d))
* Handle percent sign in player names ([`276cac5`](https://github.com/mcbeet/mecha/commit/276cac5131542e018a0b19dcd44cbe5b5c15f9fc))

## v0.5.1 (2021-10-09)
### Fix
* Update tokenstream to handle windows line endings ([`6d780dd`](https://github.com/mcbeet/mecha/commit/6d780dd11deb98b3fd9d44124439a051eba6275c))

## v0.5.0 (2021-09-29)
### Feature
* Add compilation database and refactor compile method ([`18d7b7f`](https://github.com/mcbeet/mecha/commit/18d7b7f2fc747e73bbb877b2a558abac1939ea0b))

## v0.4.0 (2021-09-26)
### Feature
* Add diagnostics, beet plugin, and basic linter ([`93fe177`](https://github.com/mcbeet/mecha/commit/93fe177cccc5635876ab388740380f17a42beecf))

### Fix
* Make it possible to configure the version ([`67ff495`](https://github.com/mcbeet/mecha/commit/67ff49560e72f4a8d04626c7a9ffca67cf676188))

## v0.3.6 (2021-09-21)
### Fix
* Proper rule baking ([`38e03fb`](https://github.com/mcbeet/mecha/commit/38e03fbd963237293671b2f5d0d47aed4ef1cf48))
* Also disambiguate when not in multiline mode ([`ee8e747`](https://github.com/mcbeet/mecha/commit/ee8e747ccd1c0724607b180259635c1b9c639453))

## v0.3.5 (2021-09-21)
### Fix
* Allow # and $ at the beginning of fake player names ([`4b7fc56`](https://github.com/mcbeet/mecha/commit/4b7fc56b5e6d7462aee2acda5de9754d0b821f47))

## v0.3.4 (2021-09-21)
### Fix
* Make it possible to provide a dict to add_commands ([`29b94f5`](https://github.com/mcbeet/mecha/commit/29b94f5712da74c0d346553c237a513ebe0910c2))

## v0.3.3 (2021-09-21)
### Fix
* Allow specifying version with dots ([`e4c9ba6`](https://github.com/mcbeet/mecha/commit/e4c9ba6256bc3ad803984a6a7bc68844b57c391a))

## v0.3.2 (2021-09-21)
### Fix
* Separate reducer and mutating reducer ([`730792c`](https://github.com/mcbeet/mecha/commit/730792c3297ad5e574ea5ff75a8463563f51b770))

## v0.3.1 (2021-09-21)
### Fix
* Remember current line indentation for the following terms ([`9691684`](https://github.com/mcbeet/mecha/commit/9691684532a30aba2b71fb3b4ec824c26889de96))

## v0.3.0 (2021-09-19)