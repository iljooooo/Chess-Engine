# CHESS ENGINE
The files implement two little snippets that allow you to play chess. Currently, the project is still incomplete, but at current commit stage you are allowed to play following the classical game rules. The only exception is the handling of the moves of a king when in check. Further developments that are planned are:
- Fixing king moves under checks mechanics
- Adding various graphical features
- Expliciting checkmate or stalemate when a game is finished
- Adding an AI Class that will be able to act as a player
- Using Reinforcement Learning to create a good enough AI-based chess engine

The project is written in pure Python using the pygame library and its extension pygame-popup, which will hopefully handle some minor graphical aspects, including a basic menu to pick between color palettes, pick the AI level, and other stuff. 

The project was created as a little funny snippet in order to familiarize a little bit with a codebase a little more complex than a school-level snippet. More details will emerge as the project grow in dimension, stay tuned!

## CURRENT TODO LIST
At current stage, these are the following operations that I plan to add in the nearby future:
- Introduce more complex graphical elements standard, like buttons that open settings environment (curtain button?)
- Improve the theme handling by directly accessing single constant variables defined in the global env.
- Complete the settings menu, introduce global control over some graphical informations about the pieces
- Review current pawn promotion move handling: at current stage, the 'CPU' is not able to see the potential of promotion, the logic is handled in the ChessMain.py. This may cause problems during the development of AI aiming to play the game
- Interlace ChessMain.py with the current main.py file, specifically let global graphical details being handled by the main, while being adapted by the already working code in ChessMain
- Add an AI.py file that allows for an AI to detect valid moves, allowing for player vs CPU, but also for CPU vs CPU games. This of course passes for some changes in the current logic of ChessMain, and possibly will require a Player class. In that context, AI is just a specific instance of Player
- Introduce different type of AIs to play the game: of course the first one is gonna be the random move AI, and more of those will be considered at different development stage.
- Actually train an AI model to play chess! Reinforcement learning here we come.
- We could consider storing specific parameters proper of a certain model at different stages of our development. These configurations could result in different level of difficulties between those to select by a player while interacting with the settings.