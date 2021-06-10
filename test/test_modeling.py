import pytest
import numpy as np
from src.ingest import Ingest
from src.modeling import OfflineModeling

ingest = Ingest()
data = ingest.download_data_from_s3()[0]
fa, ca = ingest.download_model_from_s3()


def test_cluster_happy():
    """test generated clusters are the same for models saved in s3 and newly trained models."""
    # training
    models = OfflineModeling()
    models.fa.fit(data.iloc[:, 1:164])
    data_transformed = models.fa.transform(data.iloc[:, 1:164])
    models.ca.fit(data_transformed)

    # predictions
    new_data = np.ones((1, 163))
    # predictions - true
    new_data_transformed = fa.transform(new_data)
    cluster_true = ca.predict(new_data_transformed)
    # predictions - test
    new_data_transformed2 = models.fa.transform(new_data)
    cluster_test = models.ca.predict(new_data_transformed2)

    assert cluster_test[0] == cluster_true[0]


def test_cluster_unhappy():
    """Test data with wrong dimensions generate error."""
    with pytest.raises(ValueError):
        fa.transform(data)
