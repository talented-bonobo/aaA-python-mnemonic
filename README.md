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

signed hash of aaA.py:

signature: IOuymG6bcx8dkH86WlsY8TPE1JxHlwmdx6h2a73pc38mL4QULqQQynD/GWDTdPGY09SmHfm7C356aE4y1HX2wwk=
address: N6BB8y2e4sRXSGN94zedSVaiZQUfYbqL7M
message: 19ae61d224e663a3c20dcf45d386ad522b4d3c13d8da228945c135cd0bae05c3
