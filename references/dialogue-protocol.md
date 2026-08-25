# Dialogue protocol for a problem the user cannot describe

## Goal

Turn a vague sense of difficulty into a testable problem statement without diagnosing or overwhelming the user.

## One-question loop

1. Ask for one recent concrete episode using one short prompt. Collect only one missing item per turn; do not combine what happened, when, what the user did, and how it felt into a compound question.
2. Establish enough of the relevant event, action, and result to distinguish plausible explanations before asking why. Use facts already provided; ask only for one missing fact that could materially change the analysis. Treat any cause, motive, or psychological explanation as a hypothesis to test, not a fact.
3. On later turns, ask about one missing element at a time: trigger, action, immediate payoff, delayed cost, or an exception.
4. If the answer stays vague, explicitly offer one fill-in sentence stem using labeled brackets instead of underscore blanks:

   `When [specific event] happened, I did [action]; it helped me get or avoid [immediate payoff] for the moment, but later it cost [later cost].`

5. Reuse the user's words. Do not replace them with psychological labels.
6. Apply the information-gain stop in [evidence-safety.md](evidence-safety.md). Increment the no-gain count when a response adds none of the three qualifying signals; reset it when any one appears. At a count of two, state that the evidence limit has been reached, stop explanatory analysis, and use the required explicit listening message. Do not invent another explanation.
7. After five answers, summarize:
   - observed facts;
   - self-reported feelings;
   - up to three candidate explanations;
   - evidence and counterevidence for each;
   - missing information and confidence.
8. Ask the user to correct the summary before continuing.

## Problem statement

Stop clarifying when the evidence supports a statement containing a concrete trigger, behavior, short-term payoff, long-term cost, current hypothesis, and counterexample. Write the statement as complete prose; do not leave labels or blanks in the final sentence.

Then propose one reversible seven-day experiment and the observable result that would support or weaken the hypothesis.

## Boundaries

- Do not ask multiple personal questions in one turn.
- One question mark is not enough if the sentence still requests several answers.
- Do not infer a hidden fear because the user cannot articulate a problem.
- If the user's account suggests severe distress, self-harm, inability to function, or a medical concern, stop the analysis and encourage appropriate professional or emergency support.
