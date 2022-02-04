## How to Run

(For WSL, run XLaunch and set your display variable: `export DISPLAY="127.0.0.1:0.0"`)

echo $DISPLAY

## Heuristic Function:

- Most amount of pieces (ratio?)
- Mobility (number of possible moves we have)
- Corner Pieces (and negative weight to the pieces that will give away corners)
