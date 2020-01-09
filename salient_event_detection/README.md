## Summary

This folder contains code to train models classifying salient events in the PHYRE dataset. For each collsion, inputs are the time step, each objects' shape, X/Y positions, X/Y velocities, and angle. This totals 13 input features. A positive classifier, decision tree, and support vector classifier are used. For each, a confusion matrix and tabular report are generated.

## Usage
Simply run the python file and view the printed results.
```bash
python salient.py
```
