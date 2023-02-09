<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import type { Ref } from 'vue';

const solver_url = 'https://solve4x.gothink.dev/';

const numbers = ref('');
const solutions: Ref<Array<string>> = ref([]);
const fetchErr = ref('');
const inputErr = ref('');
const show = ref(false);
const status = ref('preloaded');

interface ExcludeMap {
    '(': boolean,
    '+': boolean,
    '-': boolean,
    '*': boolean,
    '/': boolean,
}

const excludes: ExcludeMap = reactive({
    '(': false,
    '+': false,
    '-': false,
    '*': false,
    '/': false,
});

const parsed_solutions = computed(() => {
    if (Object.values(excludes).includes(true)) {
        return solutions.value.filter((sol) => (
            Object.keys(excludes).filter((k) => excludes[k as keyof ExcludeMap]).every((ex: string) => !sol.includes(ex))
        ));
    }
    return solutions.value;
});

async function getSolutions() {
    show.value = false;
    inputErr.value = '';
    fetchErr.value = '';
    let num_count = 0;

    numbers.value.split('').forEach((n) => {
        if (parseInt(n) > 0 && parseInt(n) < 10) {
            num_count++;
        }
    });

    if (num_count !== 4 || num_count !== numbers.value.length) {
        inputErr.value = "Input must be 4 digits";
        return;
    }

    status.value = 'loading';
    let response = await fetch(solver_url + numbers.value, { method: 'POST' });

    if (response.ok) {
        solutions.value = await response.json();
        status.value = 'loaded';
    }
    else {
        fetchErr.value = await response.text();
        status.value = 'preloaded';
    }
}

function toggleExclude(sym: string) {
    excludes[sym as keyof ExcludeMap] = !excludes[sym as keyof ExcludeMap];
}

function randomNumbers() {
    let nums = '';
    for (let i = 0; i < 4; i++) {
        nums += Math.floor(Math.random() * 10).toString();
    }
    numbers.value = nums;
    getSolutions();
}

</script>
<template>
    <div class="grid grid-flow-row max-w-fit justify-center justify-items-center outline outline-1 outline-blue p-4 rounded-md">
        <span class="p-1 text-lg text-center">Enter a 4-digit number or click Random</span>
        <div class="flex flex-1 justify-center">
            <input class="bg-mantle w-36 p-1 m-1 rounded-lg border border-blue text-center" v-model="numbers" type="text" placeholder="1234" name="numbers">
            <button class="bg-mantle border-2 border-flamingo rounded-lg py-1 px-2 m-1" @click="getSolutions">Solve</button>
            <button class="bg-mantle border-2 border-flamingo rounded-lg py-1 px-2 m-1" @click="randomNumbers">Random</button>
        </div>
        <div class="text-red">{{ inputErr }}</div>
        <div>{{ fetchErr }}</div>
        <div v-if="status == 'loaded'">
            <div class="flex flex-1 p-1 m-1 items-center">
                <div>Toggle:</div>
                <button :class="excludes['('] ? 'border-overlay2' : 'border-flamingo'" class="bg-mantle border-2 rounded-full px-2 pb-1 mx-1 w-8" @click="toggleExclude('(')">
                    ()
                </button>
                <button :class="excludes['+'] ? 'border-overlay2' : 'border-flamingo'" class="bg-mantle border-2 rounded-full px-2 pb-0.5 pt-0.5 mx-1 w-8" @click="toggleExclude('+')">
                    +
                </button>
                <button :class="excludes['-'] ? 'border-overlay2' : 'border-flamingo'" class="bg-mantle border-2 rounded-full px-2 pb-1 mx-1 w-8" @click="toggleExclude('-')">
                    -
                </button>
                <button :class="excludes['*'] ? 'border-overlay2' : 'border-flamingo'" class="bg-mantle border-2 rounded-full px-2 pt-1 mx-1 w-8" @click="toggleExclude('*')">
                    *
                </button>
                <button :class="excludes['/'] ? 'border-overlay2' : 'border-flamingo'" class="bg-mantle border-2 rounded-full px-2 pb-0.5 pt-0.5 mx-1 w-8" @click="toggleExclude('/')">
                    /
                </button>
            </div>
            <div class="flex flex-1 justify-center items-baseline">
                Solutions: <span class="font-bold text-lg mx-1">{{ parsed_solutions.length }}</span>
                <button class="bg-mantle border-2 border-flamingo rounded-lg px-1 pb-0.5 mx-2" v-if="parsed_solutions.length" @click="show=!show">
                    {{ show ? 'Hide' : 'Show' }}
                </button>
            </div>
            <div v-if="show">
                <ul>
                    <li class="my-1" v-for="solution in parsed_solutions">
                        {{ solution }}
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>