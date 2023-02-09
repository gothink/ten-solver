use serde::{Serialize, Deserialize};
use worker::*;
use std::collections::HashMap;

mod eq_map;
mod utils;

fn generate_map(num_arr: &Vec<i32>) -> (Vec<i32>, i32) {
    // Create a HashMap to store the frequency of each integer
    let mut freq_map: HashMap<i32, i32> = HashMap::new();
    for i in num_arr.iter() {
        *freq_map.entry(*i).or_insert(0) += 1;
    }
    // Get the unique integers and sort them by frequency
    let mut unique_ints: Vec<i32> = freq_map.keys().cloned().collect();
    unique_ints.sort_by_key(|i| freq_map[i]);

    let mut pattern: i32 = if unique_ints.len() < 3 {
        unique_ints.len() as i32 - 1
    } else {
        unique_ints.len() as i32
    };

    if unique_ints.len() == 2 {
        let first_number = unique_ints[0];
        if freq_map[&first_number] < 3 {
            pattern += 1;
        }
    }
    // Return the sorted unique integers and the length of the array
    (unique_ints, pattern)
}

fn eval_postfix(pfix: &str, vmap: &Vec<i32>) -> f32 {
    // Create a stack to store the values for RPN evaluation
    let mut stack: Vec<f32> = vec![];
    // Iterate through the input string
    for c in pfix.chars() {
        match c {
            'a' | 'b' | 'c' | 'd' => stack.push(vmap[c as usize - 'a' as usize] as f32),
            '+' => {
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                stack.push(a + b);
            }
            '-' => {
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                stack.push(a - b);
            }
            '*' => {
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                stack.push(a * b);
            }
            '/' => {
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                if b == 0.0 {
                    return 0.0 as f32;
                }
                stack.push(a / b);
            }
            _ => {}
        }
    }
    // Return the result of the RPN evaluation
    stack.pop().unwrap()
}

fn get_solutions(pattern: usize, vmap: &Vec<i32>) -> Vec<String> {
    let mut solutions: Vec<String> = vec![];
    for i in 0..eq_map::PF_LIST[pattern].len() {
        let result = eval_postfix(eq_map::PF_LIST[pattern][i], &vmap);
        if result == 10.0 {
            let equation = eq_map::EQ_LIST[pattern][i];
            let mut solution = String::new();
            for c in equation.chars() {
                match c {
                    'a' => solution.push_str(&vmap[0].to_string()),
                    'b' => solution.push_str(&vmap[1].to_string()),
                    'c' => solution.push_str(&vmap[2].to_string()),
                    'd' => solution.push_str(&vmap[3].to_string()),
                    _ => solution.push(c),
                }
            }
            solutions.push(solution);
        }
    }
    return solutions;
}

#[event(fetch)]
pub async fn main(req: Request, env: Env, _ctx: worker::Context) -> Result<Response> {
    utils::set_panic_hook();

    let router = Router::new();

    #[derive(Serialize, Deserialize)]
    struct CachedSolutions(Vec<String>);

    router
        .post_async("/:num", |_req, ctx| async move {
            if let Some(num) = ctx.param("num") {
                let mut num_arr: Vec<i32> = vec![];
                for n in num.chars() {  
                    if n.is_numeric() {
                        num_arr.push(n.to_digit(10).unwrap() as i32);
                    } else {
                        return Response::error("Invalid input", 403);
                    }
                }

                if num_arr.len() == 4 {
                    num_arr.sort();
                    let num_str: String = num_arr.iter().map(|n| n.to_string()).collect::<String>();
                    let kv = ctx.kv("SOLVER_KV")?;
                    let cors = Cors::default().with_origins("*".chars());
                    return match kv.get(&num_str).json::<CachedSolutions>().await? {
                        Some(cached_solutions) => Response::from_json(&cached_solutions)?.with_cors(&cors),
                        None => {
                            let (vmap, pattern) = generate_map(&num_arr);
                            let solutions = get_solutions(pattern as usize, &vmap);
                            let sol_str = serde_json::to_string(&solutions).unwrap();
                            kv.put(&num_str, &sol_str)?.execute().await?;
                            return Response::from_json(&solutions)?.with_cors(&cors);
                        }
                    }
                }
            }

            Response::error("Invalid input", 403)
        })
        .run(req, env)
        .await
}
