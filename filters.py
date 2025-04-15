class Filter:
    """
    Abstract class for filters.
    This class defines the interface for all filters.
    """
    @staticmethod
    def apply(prices: list[float]) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")
    

class Filter3Days(Filter):
    """
    Filter that checks if the stock price has declined in the last 3 days.
    """
    @staticmethod
    def apply(prices: list[float]) -> bool:
        for i in range(1, len(prices)):
            if prices[i - 1] > prices[i]:
                return False
        return True
    

class Filter5Days(Filter):
    """
    Filter that checks if the stock price has declined more than twice in the last 5 days.
    """
    @staticmethod
    def apply(prices: list[float]) -> bool:
        declines = 0
        for i in range(1, len(prices)):
            if prices[i - 1] > prices[i]:
                declines += 1
        return declines <= 2

