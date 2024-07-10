from typing import List, Union
from trl import SFTTrainer
import optuna
from transformers.trainer_utils import HPSearchBackend, BestRun, PREFIX_CHECKPOINT_DIR, default_compute_objective
import os
import gc
import torch


class CustomSFTTrainer(SFTTrainer):

    @staticmethod
    def run_hp_search_optuna(trainer, n_trials, direction, **kwargs):

        def _objective(trial, checkpoint_dir=None):
            checkpoint = None
            if checkpoint_dir:
                for subdir in os.listdir(checkpoint_dir):
                    if subdir.startswith(PREFIX_CHECKPOINT_DIR):
                        checkpoint = os.path.join(checkpoint_dir, subdir)
            #################
            # UPDATES START
            #################
            if not checkpoint:
                # free GPU memory
                del trainer.model
                gc.collect()
                torch.cuda.empty_cache()
            trainer.objective = None
            trainer.train(resume_from_checkpoint=checkpoint, trial=trial)
            # If there hasn't been any evaluation during the training loop.
            if getattr(trainer, "objective", None) is None:
                metrics = trainer.evaluate()
                trainer.objective = trainer.compute_objective(metrics)
            return trainer.objective

        timeout = kwargs.pop("timeout", None)
        n_jobs = kwargs.pop("n_jobs", 1)
        study = optuna.create_study(direction=direction, **kwargs)
        study.optimize(_objective, n_trials=n_trials,
                       timeout=timeout, n_jobs=n_jobs)
        best_trial = study.best_trial
        return BestRun(str(best_trial.number), best_trial.value, best_trial.params)

    def hyperparameter_search(
        self,
        hp_space,
        n_trials,
        direction,
        compute_objective=default_compute_objective,
    ) -> Union[BestRun, List[BestRun]]:

        self.hp_search_backend = HPSearchBackend.OPTUNA
        self.hp_space = hp_space
        self.hp_name = None
        self.compute_objective = compute_objective
        best_run = CustomSFTTrainer.run_hp_search_optuna(
            self, n_trials, direction)
        self.hp_search_backend = None
        return best_run
