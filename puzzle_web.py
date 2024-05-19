import streamlit as st
from simpleai.search import astar, SearchProblem
import random
import time

# Helper Functions
def list_to_string(input_list):
    return '\n'.join(['-'.join(x) for x in input_list])

def string_to_list(input_string):
    return [x.split('-') for x in input_string.split('\n')]

def get_location(rows, input_element):
    for i, row in enumerate(rows):
        if input_element in row:
            return i, row.index(input_element)

def generate_solvable_state(goal, moves=100):
    state = string_to_list(goal)
    row_empty, col_empty = get_location(state, 'e')
    for _ in range(moves):
        possible_moves = []
        if row_empty > 0:
            possible_moves.append((row_empty - 1, col_empty))
        if row_empty < 2:
            possible_moves.append((row_empty + 1, col_empty))
        if col_empty > 0:
            possible_moves.append((row_empty, col_empty - 1))
        if col_empty < 2:
            possible_moves.append((row_empty, col_empty + 1))

        move = random.choice(possible_moves)
        state[row_empty][col_empty], state[move[0]][move[1]] = state[move[0]][move[1]], state[row_empty][col_empty]
        row_empty, col_empty = move

    return list_to_string(state)

# Constants
GOAL = '1-2-3\n4-5-6\n7-8-e'
goal_positions = {number: get_location(string_to_list(GOAL), number) for number in '12345678e'}

# Puzzle Solver Class
class PuzzleSolver(SearchProblem):
    def __init__(self, initial_state):
        super().__init__(initial_state=initial_state)

    def actions(self, state):
        rows = string_to_list(state)
        row_empty, col_empty = get_location(rows, 'e')
        actions = []
        if row_empty > 0:
            actions.append(rows[row_empty - 1][col_empty])
        if row_empty < 2:
            actions.append(rows[row_empty + 1][col_empty])
        if col_empty > 0:
            actions.append(rows[row_empty][col_empty - 1])
        if col_empty < 2:
            actions.append(rows[row_empty][col_empty + 1])
        return actions

    def result(self, state, action):
        rows = string_to_list(state)
        row_empty, col_empty = get_location(rows, 'e')
        row_new, col_new = get_location(rows, action)
        rows[row_empty][col_empty], rows[row_new][col_new] = rows[row_new][col_new], rows[row_empty][col_empty]
        return list_to_string(rows)

    def is_goal(self, state):
        return state == GOAL

    def heuristic(self, state):
        rows = string_to_list(state)
        distance = 0
        for number in '12345678e':
            row_new, col_new = get_location(rows, number)
            row_goal, col_goal = goal_positions[number]
            distance += abs(row_new - row_goal) + abs(col_new - col_goal)
        return distance

# Streamlit App
def app():
    st.title('Puzzle Solver')
    
    if 'state' not in st.session_state:
        reset_session()

    if st.button('Shuffle'):
        reset_session()

    if st.button('Solve'):
        solver = PuzzleSolver(st.session_state.state)
        start_time = time.time()
        result = astar(solver)
        end_time = time.time()
        if result:
            st.session_state.solution_steps = [step[1] for step in result.path()]
            st.session_state.current_step = 0
            st.session_state.show_all_steps = False
            st.session_state.solve_time = end_time - start_time
            st.session_state.auto_mode = False

    st.subheader("Current Puzzle State")
    display_puzzle(st.session_state.state if 'state' in st.session_state else '')

    if st.session_state.get('solution_steps'):
        st.write(f"Solved in {len(st.session_state.solution_steps) - 1} steps")
        st.write(f"Time taken: {st.session_state.solve_time:.2f} seconds")
        navigation_buttons()

    if st.session_state.get('show_all_steps'):
        st.write("All Steps:")
        for index, step in enumerate(st.session_state.solution_steps):
            st.subheader(f"Step {index + 1}")
            display_puzzle(step)

def navigation_buttons():
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    if col1.button('Previous Step'):
        if st.session_state.current_step > 0:
            st.session_state.current_step -= 1
    if col2.button('Next Step'):
        if st.session_state.current_step < len(st.session_state.solution_steps) - 1:
            st.session_state.current_step += 1

    with col3:
        if st.session_state.show_all_steps:
            if st.button('Collapse Steps'):
                st.session_state.show_all_steps = False
                st.rerun()
        else:
            if st.button('Show All Steps'):
                st.session_state.show_all_steps = True
                st.rerun()

    if 'solution_steps' in st.session_state and st.session_state.solution_steps:
        with col4:
            if st.button('Auto'):
                st.session_state.auto_mode = True

    # Display the current step after buttons to ensure immediate update
    if st.session_state.auto_mode:
        auto_display_steps()
    elif not st.session_state.show_all_steps:
        st.subheader(f"Step {st.session_state.current_step + 1} of {len(st.session_state.solution_steps)}")
        display_puzzle(st.session_state.solution_steps[st.session_state.current_step])

def auto_display_steps():
    placeholder = st.empty()
    for step in range(st.session_state.current_step, len(st.session_state.solution_steps)):
        st.session_state.current_step = step
        with placeholder.container():
            st.subheader(f"Step {st.session_state.current_step + 1} of {len(st.session_state.solution_steps)}")
            display_puzzle(st.session_state.solution_steps[st.session_state.current_step])
            time.sleep(1)
    st.session_state.auto_mode = False
    st.rerun()  # Refresh to update mode status

def reset_session():
    st.session_state.state = generate_solvable_state(GOAL, 100)
    st.session_state.solution_steps = []
    st.session_state.current_step = 0
    st.session_state.show_all_steps = False
    st.session_state.auto_mode = False

def display_puzzle(state):
    grid = string_to_list(state)
    cols = st.columns(3)
    for row in grid:
        for col_index, val in enumerate(row):
            color = "#aaaaaa" if val == 'e' else "#3333ff"
            button_html = f"""
            <div style='
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100px;
                height: 100px;
                font-size: 26px;
                color: white;
                background-color: {color};
                border: 2px solid black;
                margin: 2px;
                box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.2);
                border-radius: 10px;
                '>{val if val != 'e' else ''}</div>
            """
            cols[col_index].markdown(button_html, unsafe_allow_html=True)

if __name__ == '__main__':
    app()
