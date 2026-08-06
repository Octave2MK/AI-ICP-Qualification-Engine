from app.acquisition.batch.batch_processor import (
    BatchProcessor,
)

from app.acquisition.acquisition_models import (
    ICP,
)



class FakePipeline:

    def run(
        self,
        icp,
    ):

        return [
            icp.job_titles[0]
        ]



def test_batch_runs_multiple_icps():

    processor = BatchProcessor(
        FakePipeline()
    )


    results = processor.run(
        [
            ICP(
                job_titles=[
                    "Business Coach"
                ],
                countries=[
                    "France"
                ],
            ),

            ICP(
                job_titles=[
                    "Marketing Consultant"
                ],
                countries=[
                    "Belgium"
                ],
            ),
        ]
    )


    assert len(results) == 2

    assert (
        results[0]
        ==
        "Business Coach"
    )