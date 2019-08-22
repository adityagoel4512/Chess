AdiChess
========

A simple purely Python chess engine.
Inspired by Sunfish, it's designed to be extremely an short and readable implementation
of a chess engine and very tunable too.

Board Representation
--------------------
Object array.

I've opted to not go for a bitboard representation to make the program as short and simple as possible, even at the
expense of speed of the engine.

Search
------

* Shallow move ordering
* Transposition Table
* Quiescence Search

Evaluation
----------

* Material
* Piece square tables
* Mobility
* Pawn Structure
* Defence attack symmetries
* King Safety
* Bonuses (double bishops, promotions, castling)

To play the engine, run play.py - command line argument 1 is the minimax search depth, 2 is the side to play as.