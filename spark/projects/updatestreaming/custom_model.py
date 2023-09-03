

class CustomModel:
    """
    Custom model class that imitate a real ML model.

    :param is_cloned: The number of times to repeat an item value.
    """

    def __init__(self):
        self.is_cloned = True

    def fit(self, is_cloned):
        if not isinstance(self.is_cloned, bool):
            raise Exception("is_cloned is not boolean.")
        self.is_cloned = is_cloned

    def transform(self, item):
        """
        Transform input value based on parameter is_cloned.

        :param item: Input item.
        :return: Transformed value.
        """
        if not hasattr(self, "is_cloned"):
            raise Exception("is_cloned is not defined.")
        if self.is_cloned:
            return 3 * str(item).zfill(2)
        return str(item).zfill(2)
