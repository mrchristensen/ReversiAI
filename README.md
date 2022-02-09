## How to Run

(For WSL, run XLaunch and set your display variable: `export DISPLAY=127.0.0.1:0.0`)

(Use `echo $DISPLAY` to make sure it is there)

- To run the server (in the _ReversiServer_ dir): `java Reversi 10`
- To run the bot client (in the _ReversiBot_Python3_ dir): `python3 reversi_python_client.py localhost 1`
- To run the human client (in the _ReversiHuman_ dir): `java Human localhost 2`
- To run the random client (in the _ReversiRandom_Java_ dir): `java RandomGuy localhost 2`
  - (or `python RandomGuy.py localhost 2` in the _ReversiRandom_Python_ dir)

## Heuristic Function:

- Most amount of pieces (ratio?)
- Mobility (number of possible moves we have)
- Corner Pieces (and negative weight to the pieces that will give away corners)
