# Solve 4 X

This project contains the code referenced in my *ChatGPT: Total game-changer, still no I in AI* blog posts ([Part 1](https://gothink.dev/blog/chatgpt-algo-pt-1/) / [Part 2](https://gothink.dev/blog/chatgpt-algo-pt-1/)).

The goal was to create an algorithm to solve a unique problem so that I could generate hints for the game `4=10`. I initially tried to see if I could get ChatGPT to write the algorithm for me, but ultimately failed. The remainder of the project was built while using ChatGPT as a sort of assistant, with mixed results. In the end, very little of the code appearing in this project was actually produced by ChatGPT.

## Contents

- `util` contains a python script for generating an equation map.
- `workers` contains the Cloudflare Workers for solving the equations.

These were based on templates provided by Cloudflare ([github](https://github.com/cloudflare/templates)). Note: the `solver-emscripten` worker doesn't currently build, but the C code itself runs fine.

- `component` contains the vue.js web component that connects to the workers API and provides hints based on the solutions it receives from the worker.

Please keep in mind this is a clunky, over-engineered solution that was built as a fun project to test the capabilities and limitations of ChatGPT, and tinker with novel technologies.