from pathlib import Path
from typing import Callable
import pandas as pd
import numpy as np
from collections import namedtuple
import calliope


class Processor:
    """A class to process and collect calliope model data."""
    def __init__(self, function: Callable):
        """
        Parameters
        ----------
        function : Callable
            A function that expects a calliope.Model and returns a pd.DataFrame.
        """
        self.results = pd.DataFrame()
        self.function = function
        
    def process(self, model: calliope.Model, **kwargs) -> None:
        """
        Apply the function to a calliope model and concatenate the result to self.results.

        Parameters
        ----------
        model : calliope.Model
            A calliope model to process.
        **kwargs : dict
            Additional attributes used as extra columns in the results DataFrame.
        """
        result = self.function(model)
        for key, value in kwargs.items():
            result.insert(0, key, value)

        self.results = self._standardise_and_concat([self.results, result])
        
    @staticmethod
    def _standardise_and_concat(dfs: list[pd.DataFrame]) -> pd.DataFrame:
        """Standardize and concatenate a list of DataFrames."""
        all_columns = [col for df in dfs for col in list(df.columns)]
        all_columns = list(dict.fromkeys(all_columns))  # like set operation, but conserve order
        dfs_standardized = [df.reindex(columns=all_columns, fill_value=np.nan) for df in dfs]
        concatenated = pd.concat(dfs_standardized, ignore_index=True)

        return concatenated


class Postprocessor:
    """
    Class that iterates over several calliope.Models and processes them
    with registered processors.

    Parameters
    ----------
    model_specs : list[namedtuple]
        List of namedtuples with model specifications.
        Each namedtuple should contain the same fields.
        The fields can be any, but one of them must be path.
        The path should point to a calliope model file.
    
    Methods
    -------
    add_processor(processor: Processor) -> None
        Add a Processor instance to registered processors.
    
    process_results() -> None
        Process the results using the registered processors.
    
    _validate_model_spec(model_specs: list[namedtuple]) -> list[namedtuple]
        Validate the model specifications and check for file existence.
    """
    def __init__(self, model_specs: namedtuple):
        self.model_specs = self._validate_model_spec(model_specs)
        self.processors = []

    def add_processor(self, processor: Processor) -> None:
        """Add a processor instance to the list of registered processors."""
        if not isinstance(processor, Processor):
            raise TypeError("Processor must be of type 'Processor'.")
        self.processors.append(processor)
        
    def process_results(self):
        """Iterate over all models and let all registered processors process."""
        for model_spec in self.model_specs:
            model = calliope.read_netcdf(model_spec.path)
            attributes = {k: getattr(model_spec, k) for k in model_spec._fields if k != 'path'}
            for processor in self.processors:
                processor.process(model, **attributes)
    
    @staticmethod
    def _validate_model_spec(model_specs: list[namedtuple]) -> list[namedtuple]:
        """Make sure all model specs are of the same type and path exists."""
        model_specs_type = type(model_specs[0])
        for model_spec in model_specs:
            if not isinstance(model_spec, model_specs_type):
                raise TypeError(f"Model specifications must be of the same type.")
            if not hasattr(model_spec, 'path'):
                raise ValueError(f"model_spec {model_spec} is missing a 'path' attribute.")
            if not model_spec.path or not Path(model_spec.path).exists():
                raise FileNotFoundError(f"File not found: {model_spec.path}")
        return model_specs
