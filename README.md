# AITDLearning
TD Learning, HW6

Specifications:
1. The Antics state space is too big to learn in a short period of time. So you’ll need a way
to consolidate it. Design an approach for categorizing your state space into one of a
relatively small number of states. My best guess is that a good target would be on the
order of tens of thousands of states. (An agent will see only a small fraction of these in
any given game.) Think carefully about your design for this consolidation as it is critical
to the success of your agent. You should be prepared to try multiple designs to see which
works best. See me if you need some advice on this but I'd prefer you tackled it on your
own so that there are a variety of designs.

2. Write a method that takes an Antics state and returns a consolidated state as per your
design.

3. Use a list (or other data structure) to keep track of the utility to each consolidated state
your agent has encountered so far. (Hint: Don’t add states to the list until you need
them! This will save you a lot of time and space.)

4. Write save and load methods to save the current state-utility list to a file and load the
from a file respectively. Use a hard-coded filename that contains your UP userid.

5. Each time your agent completes a game, save your current state utilities to a file. When
the agent runs its first game after startup, it should look to see if a file is there and, if so,
initialize the consolidated state utilities list with the values from the file. (Caveat: When
testing your agent, don't forget to delete this file when you need to reset the agent.)

6. Decide on a reward function for your agent. A good default is to use +1 for winning, -1
for losing and a tiny negative number (say -0.01) for everything else. However, I can
think of other approaches that might (or might not!) work better.

7. Select a discount factor () for your TD-Learning algorithm. I recommend you start with
a value slightly less than 1.0 and then try different values later.

8. Select an equation for the learning rate (α) for your TD-Learning algorithm. You can set
this to a large number (say 0.99) that declines over time to near zero. It should decline
quickly at first and more slowly later (think exponential). Alternatively you can just fix
your learning rate at a tiny amount. The former might lead to faster learning. Consider
experimenting with different learning rates.

9. Each time the agent makes a move, use TD-Learning to adjust the utility of the previous
state. You may want to consider updating the utilities of the previous N states to speed up
the learning.

10. Your agent should use the learned utilities to decide what actions to take (active learning).
Specifically, select the action that leads to the state with the highest utility. You can do
this in a number of ways:
a. The easiest way to do this is to just use the prediction method you wrote for the
uninformed search agent that determines what the state would look like after the
agent takes a given move. Thus, you can predict the outcome of an action.
b. The above method does not take into account the opponent's move. As an
alternative, you can use your revised state prediction method from the minimax
assignment that guesses the opponent's move by using applying the agent's
knowledge as if it were its own opponent.
c. You can construct a transition function (T(s,a,s')) lookup table based upon the
agent's experiences. This function will log the results of taking certain actions in
certain states and, thus, can be used to predict the outcome of a particular action
over time.
d. Another option is to eliminate your model entirely. Instead, learn over Q-values
(state-action pairs) as discussed in class. This will require more training but may
give a more satisfying result as you are not giving the agent any free knowledge
about how the environment works.

11. (optional) You can greatly speed the rate at which your agent learns by using eligibility
traces as was discussed in lecture. Each entry in your list of utilities for each state will
also need an eligibility value.

12. Your final agent must reliably complete a game with a random player in 3 minutes or less
when playing on a lab computer. In addition, your agent must always be able to complete
a game when playing against itself. Finally, your agent should reliably defeat a random
agent more than 60% of the time.
