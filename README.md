# Project Description
This project is focused on voice leading (also called part writing) in tonal harmony. Tonal harmony has a vocabulary consisting of triads and 7th chords and a grammar consisting of the ways in which the chords are selected (harmonic progression) and connected (voice leading). The basic task in this project is to do voice leading given a harmonic progression, following the conventions and norms of tonal composers. This will require formulating the voice leading problem (rewards, state space/features) so that reinforcement strategies like value iteration can be applied. Once the problem has been properly translated, several reinforcement learning schemes can be applied and evaluated.

## Problem simplifications
1. Harmonic progression is provided, algorithm need only provide the voicings
2. We consider only harmonic progressions in the key of C major of length 4
3. We restruct the range of each part
4. We only consider triad chords without inversions

## To Do: 
1. Rule-breaking functions
    a. Voice crossing
    b. Leaps --> augmented intervals, 7ths, leaps larger than an octave
    c. Parallel motion (parallel 5ths and octaves)
        * Have to check all 6 pairs!
    d. Direct 5ths: outer parts move in the same direction into a P5 or P8 with a leap in the soprano part
2. Create "training set" of chord progressions
3. Function to convert algorithm output to MIDI

All other rules (spacing, ranges) are taken care of by the state space definition

### Data Structures
A triad chord is a set of three notes (chord tones). There are seven triad chords in the key of C major. Each of these chords has several legal voicings.  

A "voicing" is a list of four MIDI pitches `[b,t,a,s]` sorted from lowest to highest. They denote the pitches taken by the bass, tenor, alto, and soprano parts. The voicing for a given chord must contain at least one copy of each note in the triad chord, as well as one additional note that is a double of one of the chord tones. Note that there are always 4 pitches, but two of them may be identical. 

We define a dictionary `state_indices` that assigns an index to each voicing (as defined above). This allows us to use the state indices in our Q-learning algorithm.

We define a state dictionary that contains all legal states given our problem constraints. They are organized by chord number. Thus, `state_dict[chord_num]` contains a list of legal voicing indices for the given chord.

### Algorithm
The learning agent is defined in the `QLearningAgent` class. The typical Q-learning update is given by:

```
Q(state,action) = Q(state,action) + self.alpha*(reward+gamma*max(Q(next_state, actions))- Q(state,action))
```

In this problem, there are no actions. Another way of looking at it is the action is just what state you transition to next. 

The other main difference between this problem and those covered in class is that we have rewards associated with *state pairs* instead of state action pairs. A state by itself has no associated reward.

We can reformulate the problem as follows:

* We consider our "actions" to be the next state that agent transitions to. Thus, if there are `n` states, there are also `n` actions.
* Our Q-value table is `nxn`
* 


### Listening 