from app.acquisition.acquisition_models import ICP


class BatchProcessor:
    """
    Exécute plusieurs acquisitions ICP.
    """


    def __init__(
        self,
        pipeline,
    ):

        self.pipeline = pipeline



    def run(
        self,
        icps: list[ICP],
    ):

        results = []


        for icp in icps:

            prospects = self.pipeline.run(
                icp
            )

            results.extend(
                prospects
            )


        return results