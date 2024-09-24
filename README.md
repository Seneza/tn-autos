# Tennessee Auto Businesses Networks 🚛

![image](https://github.com/user-attachments/assets/fb8019a6-976b-4bdb-89fa-22e91b7ac7df)

## [Demo](https://www.loom.com/share/a2e4bd7ae5ef439a91f8d86ac027278f?sid=4cf7a528-9edd-4382-9817-4a020486ab4c)

Interactive web application built with Gradio to visualize auto businesses and population data across Tennessee. This application provides **maps**, **charts**, and **data tables** to explore **the distribution of auto-related businesses and demographic information by county, healthcare referral regions(HRRs) and HSAs**.

## Features

- **Interactive Maps**: Visualize the locations of various auto businesses across Tennessee with options to filter by zip code and business type.
- **Population Charts**: View bar charts displaying population distribution by county for the years 2010 and 2020.
- **Isochrone Maps**: Generate isochrone maps around AutoZone locations to visualize areas reachable within a specified driving time.
- **Data Tables**: Explore a curated list of auto repair and parts locations sourced from Yellowbook.

## Table of Contents

- [Features](#Features)
- [Demo](#Demo)
- [Installation](#Installation)
- [Data Sources](#data-sources)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.11 or higher
- An OpenRouteService API key (for isochrone map generation)

### Clone the Repository

```bash
git clone https://github.com/LNshuti/tn-autos.git
cd tn-autos
```

### Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements.txt**

```
branca
folium
geopandas
gradio
numpy
openrouteservice
pandas
plotly
```

## Data Sources

- **Business Locations**: Custom dataset containing locations of auto businesses in Tennessee.
- **Population Data**: U.S. Census Bureau datasets for county-level population statistics.
- **Geographic Data**: Shapefiles for Tennessee counties to render geographic boundaries on maps.

## Usage

### Run the Application

```bash
python app.py
```
The application will launch and provide a local URL `http://127.0.0.1:7860` to interact with the dashboard.

### Application Overview

- **Overview Tab**:
  - *Tennessee Population 2010*: Displays a bar chart of the 2010 population by county.
  - *Auto Repair/Parts in Tennessee*: Shows a data table of selected auto businesses.
  - *Map Output*: Interactive map displaying business locations with markers color-coded by business type.

- **Tennessee Businesses by County Tab**:
  - *Filters*: Dropdown menus to select a specific zip code and business type.
  - *Map Output*: Updates interactively based on selected filters to display relevant businesses on the map.

## Configuration

### OpenRouteService API Key

To enable isochrone map functionality, you need an API key from OpenRouteService.

1. **Obtain an API Key**: Sign up at [OpenRouteService](https://openrouteservice.org/dev/#/signup) and obtain an API key.
2. **Set the API Key as an Environment Variable**:

   ```bash
   export ORS_API_KEY='your-api-key-here'  # On Windows, use `set ORS_API_KEY=your-api-key-here`
   ```

   Alternatively, you can create a `.env` file in the project root:

   ```
   ORS_API_KEY=your-api-key-here
   ```

### Adjusting Map Settings

- **Default Location**: The map centers on Tennessee coordinates `[35.8601, -86.6602]` with a default zoom level of 8. You can adjust these settings in the `create_map` function within `app.py`.

## Stack

- **OpenRouteService** to create 30 minutes isochrone.
- **Gradio** for the interactive web interface.
- **Folium and GeoPandas** for map rendering.
- **Plotly** for data visualization.
- **U.S. Census Bureau** for population data.

# Experimentation

## **Multi-Armed Bandit Problems**

1. **What is a Multi-Armed Bandit (MAB)?**
    - A MAB problem involves several options (arms) and a decision-maker that selects which arm to pull over time to maximize some reward.
    - The challenge is to balance *exploration* (learning about different arms) and *exploitation* (choosing the best-known arm).

2. **Use Cases of MAB**
    - Digital advertising, where you allocate resources to ads.
    - Clinical trials, where different treatments need to be tested.

3. **Regret Minimization**:
    - MAB algorithms aim to minimize regret, which is the difference between the cumulative reward and the reward of the optimal strategy.

**Example**:
A small code block introducing MAB using `numpy` for a simple 2-arm bandit.

```python
import numpy as np

# Reward probabilities for two arms
reward_prob = [0.5, 0.7]

# Simulate pulling arms
np.random.binomial(1, reward_prob[0]), np.random.binomial(1, reward_prob[1])
```

---

### **Exploration vs. Exploitation in MAB**

1. **Exploration**:
    - Necessary to gather information about the arms.
    - Explores new actions, even when suboptimal, to gain knowledge.

2. **Exploitation**:
    - Uses the knowledge gained so far to maximize immediate rewards.
    - Exploits the best arm known at that moment.

3. **Balancing Exploration and Exploitation**:
    - If we only exploit, we risk never learning the best arm. If we only explore, we waste resources.

**Example**: 
Simulate 100 rounds of a random policy (pure exploration) and a greedy policy (pure exploitation).

```python
num_rounds = 100
choices = np.random.choice([0, 1], size=num_rounds)
rewards = np.random.binomial(1, [reward_prob[choice] for choice in choices])
```

---

### **Thompson Sampling for Multi-Armed Bandits**

1. **What is Thompson Sampling?**
    - A method that models the reward of each arm as a probability distribution.
    - Samples from the distribution to balance exploration and exploitation.

2. **Steps in Thompson Sampling**:
    - Sample a probability for each arm based on prior observations.
    - Select the arm with the highest sampled probability.
    - Update the posterior distribution based on the outcome.

3. **Advantages**:
    - Thompson sampling balances exploration and exploitation naturally.
    - It is computationally efficient and works well in practice.

**Example**:
Implement a basic Thompson Sampling algorithm for a 2-arm bandit.

```python
from scipy.stats import beta

successes = [0, 0]
failures = [0, 0]

def thompson_sampling_arm():
    return np.argmax([beta.rvs(1 + successes[i], 1 + failures[i]) for i in range(2)])

# Simulate pulling arms and updating rewards
for _ in range(100):
    chosen_arm = thompson_sampling_arm()
    reward = np.random.binomial(1, reward_prob[chosen_arm])
    if reward:
        successes[chosen_arm] += 1
    else:
        failures[chosen_arm] += 1
```

---

### **Contextual Bandits and Real-World Applications**

1. **What are Contextual Bandits?**
    - Unlike traditional MAB, contextual bandits take into account the state or features of the environment.
    - The goal is to map contexts to actions to maximize reward.

2. **Use Cases of Contextual Bandits**:
    - Personalized recommendations (e.g., news, ads).
    - Adaptive clinical trials where patient features are used to assign treatments.

3. **Implementing a Contextual Bandit**:
    - Contextual bandits use feature-based models (like logistic regression) to predict rewards.

**Example**:
Use `sklearn` to implement a basic contextual bandit model using logistic regression.

```python
from sklearn.linear_model import LogisticRegression

contexts = np.random.randn(100, 2)
arms = np.random.choice([0, 1], size=100)
rewards = np.random.binomial(1, arms * 0.7 + contexts[:, 0] * 0.3)

model = LogisticRegression().fit(contexts, rewards)
```

---

### **Evaluating Bandit Algorithms and Real-World Challenges**

1. **Evaluating Multi-Armed Bandit Algorithms**:
    - **Cumulative Regret**: Measure how much reward is lost by not always selecting the optimal arm.
    - **Conversion Rate**: Percentage of times the optimal arm was selected.

2. **Real-World Challenges**:
    - **Non-Stationary Rewards**: The reward probabilities may change over time.
    - **Delayed Feedback**: Rewards might not be observed immediately, complicating learning.
    - **Multiple Objectives**: In real-world systems, there might be trade-offs between multiple goals.

3. **Simulating MAB with Evaluation Metrics**:
    - Simulate a simple MAB experiment and plot the cumulative regret over time.

**Example**:
Simulate and plot cumulative regret for a Thompson Sampling policy.

```python
import matplotlib.pyplot as plt

cumulative_regret = np.cumsum([reward_prob[1] - reward_prob[thompson_sampling_arm()] for _ in range(100)])

plt.plot(cumulative_regret)
plt.title('Cumulative Regret')
plt.xlabel('Rounds')
plt.ylabel('Regret')
plt.show()
```

# Contact

Please open an issue or contact [nshutl0@sewanee.edu](mailto:nshutl0@sewanee.edu).

## License

This project is licensed under the [MIT License](LICENSE).


