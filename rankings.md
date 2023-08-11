# Ranking Algorithms

We want to be able to rank claims by order of interest, and also assign public figures a “truth score” based on how good they are at predicting things.

## Truth score

Note: The following algorithms only work on claims that have already been resolved. What you can do is to only include known outcomes and continuously update the public figure scores as claim outcomes are added or changed.

### Algorithm 1

**Problem**: we want to be able to rank public figures based on trustworthiness, i.e. the percentage of claims that they have gotten right. But figures with a very small number of claims can have 100%, so how do we combine some notion of uncertainty into this?

**Solution**: Given a public figure’s track record, for example 10 correct and 2 incorrect predictions, pretend that they made a further two predictions, one right and one wrong (making their score 11 correct and 3 incorrect = 78.6%). This is known as [Laplace’s rule of succession](https://en.wikipedia.org/wiki/Rule_of_succession); it is an equivalent problem to ranking Amazon reviewers: [3b1b Binomial Distributions](https://youtu.be/8idr1WZ1A7Q?t=107)

This solution assumes conditionally independent random variables (predictions) but this is not necessarily always the case with real world data; for example, a person might make many claims related to the same world event so they are not independent.

### Algorithm 2

**Problem**: the previous model does not take into account any notion of prior probability; for example, a person that has an opinion that always conforms to the majority opinion will probably be more likely to be right than a person that has a minority opinion. A person making five correct and one incorrect 10% predictions should be scored higher than a person making five correct and one incorrect 90% predictions.

**Solution**: for each moment in time $t$, we interpret the prior probability of an opinion being correct as the proportion of people who believe in that opinion. For example, Market 1 has resolutions 1, 2, 3. If Opinion 1 has 10 people believe in it, Opinion 2 has 80 people, and Opinion 3 has 10 people, the prior probability of Opinion 1 being correct is 10/100.

|                    |  1  |  2  |  3  |
|:------------------:|:---:|:---:|:---:|
| # people believing | 10  | 80  | 10  |
| Prior (% of total) | 0.1 | 0.8 | 0.1 |

|                    |$p_1$|$p_2$|$p_3$|
|:------------------:|:---:|:---:|:---:|
| A                  | 1   | 0   | 0   |
| B                  | 0   | 1   | 0   |

This table shows the beliefs of person A and person B about events 1, 2, and 3 at the time they predict the outcome. 1 has a prior probability of 10% of being correct, since 10% of people believe in it. Person A believes 1 will happen with 100% confidence. Person B believes 2 will happen with 100% confidence.

Weight ($w$): The idea of weights is helpful because we want correct low-probability opinions to be “valued more” than correct high-probability opinions. The weight of each prediction will be 1 minus the prior.

Prediction ($p$): the probability distribution that each person assigns to a given market’s outcome. In the example, Person A’s prediction is that there will be a 100% chance 1 will happen. I assume that for most news data, we will need to assign 100% probability to one outcome and 0 to every other since normally public figures don’t give probabilities for their predictions.

Result ($r$): a binary variable that is equal to 1 if the outcome happens and 0 otherwise, determined when the market is resolved.

Prediction score ($s_i$): equal to $\sum_{i} w_i p_i r_i$. Most of the terms are 0 except for when $r_i = 1$.

Score ($s$): a person’s total “truth score”, equal to the sum (over all markets) of their prediction scores divided by the sum of result weights. Prediction scores refer to the score from a single market/prediction, while score refers to the weighted average across all markets.

Let’s try to calculate prediction scores for example market 1.

In scenario 1, 1 is true. Person A’s prediction score for market 1 $s_1 = \sum_{1 \leq i \leq 3} w_i p_i r_i = w_1 p_1 r_1$, where $w_1 = 1 - 0.1 = 0.9$ (since 10% of people believe 1 is true when person A predicts 1), $p_1 = 1$ (since person A predicts 1 with 100% certainty), and $r_x = 1$ (since 1 happened). So $s_1 = 0.9 \cdot 1 \cdot 1 = 0.9$. Person B’s prediction score for market 1 is 0. You always get a score of 0 if you predict the outcome that happens has 0% chance of occurring.

Person A’s truth score is the sum of their prediction scores divided by the sum of their weights, which is 0.9 / 0.9 = 1 since there is only one market. Person B’s truth score is 0 / 0.9 = 0.

In scenario 2, Y is true. Person A’s prediction score is 0 while Person B’s prediction score is 0.2 * 1 * 1 = 0.2.

In scenario 3, Z is true, so Person A and B both have 0 prediction score.

Now, to prevent this algorithm from dividing by zero weights, we don’t consider predictions made in a direction with a 100% prior. For example, consider a market where 100 people believe that the sun will rise tomorrow (X), and 0 people believe that it won’t rise tomorrow (Y). If Person A predicts that the sun will rise tomorrow, we will add them to the count of people who believe X, making it 101, but we will not update their score or weights. However, if Person B predicts Y, then we will update their score as normal.

Also, to prevent the problem of people with a low number of predictions having a truth score of 100%, we will initialize their score with a correct and incorrect prediction at 50% prior, analogous to Algorithm 1. This means that without predicting anything, everyone will have an initial score of (0 + 0.5) / (0.5 + 0.5) = 50%.

Runtime: Should be fast, given a list of when people predict things

**Weaknesses**:

Like with the previous algorithm, assumes conditional independence. A person might actually have a really good track record with one topic area but might be really bad at another. In the future, one possible future extension might be to have a per-topic rating.

Works better if people give a probability distribution for outcomes, but in real life, people usually only claim one thing rather than claiming A will happen with 90% certainty and B will happen with 10%. Right now, I can’t think of an easy workaround.

Might be hard to explain if we want to make things transparent to the public. Find simpler explanation?

I haven’t worked out how to update things if someone changes their mind. We could do something like Manifold where people take profit/loss based on the delta share price between when they “bought” (made claim) and when they “sold” (changed their mind), and they “rebuy” into the market with the other option. Peoples' “balance” could be interpreted as their trust score.

## Controversy score

### Algorithm 1

Entropy can be interpreted as controversy. Entropy measures the level of unpredictability of a system; for example, if a coin flips heads 99% of the time, it has low entropy because we can have high confidence it will land heads. However, a coin has maximum entropy when it flips heads 50% of the time, since at this percentage it is the hardest to predict outcomes.

We will use entropy to measure controversy; the controversy score is simple, it is just entropy divided by max entropy. Generalizing the coin flip example, max entropy is achieved with a uniform distribution among outcomes. The closer to a uniform distribution the different versions of a claim has, the more controversial it is.

Let L be the list of numbers of people with an opinion about an issue. For example, if an issue has perspectives A, B, and C, $L$ might be [10, 20, 15]. Let’s say there are $o = 3$ different perspectives.

Let $n = \max(\sum{L}, \delta)$ be the total number of people with opinions. We use a $0 < \delta \ll 1$ to prevent division by zero which will be useful later.

For $0 \leq i < o$, let $p_i = \max(\frac{L_i}{n}, \delta)$ be the ratio of people believing in perspective i. Using the example $L = [10, 20, 15]$, $p_0 = 10/45 = 0.22…$, $p_1 = 0.44…$, $p_2 = 0.33…$

The entropy score is
$$E = \frac{\sum_{0 \leq i < o} p_i \log(p_i)}{\log(1/o)}$$
Conventionally log is in base 2, representing the number of bits. Using the example, $E = (0.22 * \log(0.22) + 0.44 * \log(0.44) + 0.33 * \log(0.33)) / \log(1/3) = 0.9656…$ [Desmos example](https://www.desmos.com/calculator/vq0bpnmp9a)

Entropy score ranges from 0 to 1, with a score of 1 indicating high controversy.

**Problems**: This is measured based on how many people have a certain opinion; it might not be the best measurement of controversy. For example, let’s say a 50/50 split of the population are on each side of the debates on government spending and abortion. However, it is intuitive to conclude that abortion is much more controversial than government spending, despite people being equally divided based on the numbers. A different algorithm could use sentiment analysis or similar techniques to measure how strongly people feel about certain issues. Or the controversy score could be a mix of different techniques.

## Interest score

Interest score is somewhat related to controversy, in that usually controversial issues are also of public interest. However, sometimes there are issues that aren’t very controversial that are still of public interest.

One measure of interest is simply the number of instances a claim has been reported on by the news. If we wanted a score between 0 and 1 we could simply do log(claim mentions) / log(max claim mentions).

See also:

[Deriving the Reddit Formula](https://www.evanmiller.org/deriving-the-reddit-formula.html)

[How Reddit Ranking Algorithms Work](https://medium.com/hacking-and-gonzo/how-reddit-ranking-algorithms-work-ef111e33d0d9)

[How Hacker News Ranking Algorithm Works](https://medium.com/hacking-and-gonzo/how-hacker-news-ranking-algorithm-works-1d9b0cf2c08d)