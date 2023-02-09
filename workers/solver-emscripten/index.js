// import the emscripten glue code
import emscripten from './build/module.js';

// this is where the magic happens
// we send our own instantiateWasm function
// to the emscripten module
// so we can initialize the WASM instance ourselves
// since Workers puts your wasm file in global scope
// as a binding. In this case, this binding is called
// `wasm` as that is the name Wrangler uses
// for any uploaded wasm module
let emscripten_module = new Promise((resolve, reject) => {
	emscripten({
		instantiateWasm(info, receive) {
			let instance = new WebAssembly.Instance(wasm, info);
			receive(instance);
			return instance.exports;
		},
	})
		.then(mod => {
			resolve({
				solutions: mod.cwrap('get_solutions', 'array', ['number', 'array', 'number'])
			});
		})
		.catch(reject);
});

async function getPatternScope(num_str) {
	if (num_str.length !== 4) return;
    let num_freq = {};
	num_str.split('').forEach(n => {
		let np = parseInt(n);
		if (np > 0 && np < 10) {
			num_freq[n] = num_freq[n] ? num_freq[n] + 1 : 1;
		}
	});

	const scope = Object.keys(num_freq).sort((a,b) => num_freq[b] - num_freq[a]);
	let pattern = scope.length;
	if (pattern < 3) pattern--;
	if (pattern == 2 && num_freq[scope[0]] == 2) pattern++; // checks for `aabb` vs `aaab`
	return { pattern, scope };
}

const init = {
	headers: {
		'Content-Type': 'application/json;charset=utf-8'
	}
};

export default {
	/**
	 * @param {Request} request
	 */
	async fetch(request) {
		let num = new URL(request.url).pathname.slice(1);
		const { pattern, scope } = getPatternScope(num);
		if (!scope) return new Response('Invalid request', { status: 403 });

		let solver = await emscripten_module;
		let solutions = solver.solutions(pattern, scope, 10);

		return new Response(JSON.stringify(solutions), init);
	},
};
