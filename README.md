# aaA-python-mnemonic
===============

Fork of reference implementation of BIP-0039: Mnemonic code for generating
deterministic keys, to use adjective adjective Animal encoding

Abstract
--------

This BIP describes the implementation of a mnemonic code or mnemonic sentence --
a group of easy to remember words -- for the generation of deterministic wallets.

It consists of two parts: generating the mnenomic, and converting it into a
hexidecimal representaion of a binary seed. This seed can be later used to generate deterministic wallets using
BIP-0032 or similar methods.

It reads from stdin to avoid leaving secrets in the system logs. It interprets input as hexidecimal if there are no spaces, and as a mnemonic if there are spaces.

The word lists were written to the namecoin blockchain from the parent utxo of N1WordListXXXXXXXXXXXXXXXXXXXbNNNP, N6BB8y2e4sRXSGN94zedSVaiZQUfYbqL7M.
