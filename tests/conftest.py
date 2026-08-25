import os

# Recorded providers are an explicit test-only seam. Normal application defaults stay live-only.
os.environ["OMNITRADE_ENV"] = "test"
os.environ["OMNITRADE_FIXTURE_MODE"] = "true"
