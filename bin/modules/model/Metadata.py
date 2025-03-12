class Metadata:
    def __init__(self, title: str, description: str, access: str, date: dict):
        self.title :str = title
        self.description = description
        self.access = access
        self.timestamp = date.get("timestamp", "")
        self.formatted_date = date.get("formatted", "")

    @classmethod
    def from_json(cls, json_data: dict):
        """
        Create an instance of Metadata from a dictionary.
        """
        return cls(
            title=json_data.get("title", ""),
            description=json_data.get("description", ""),
            access=json_data.get("access", ""),
            date=json_data.get("date", {}),
        )

    def to_dict(self):
        """
        Convert the Metadata object back to a dictionary.
        """
        return {
            "title": self.title,
            "description": self.description,
            "access": self.access,
            "date": {
                "timestamp": self.timestamp,
                "formatted": self.formatted_date,
            },
        }

    def __repr__(self):
        """
        String representation of the Metadata object.
        """
        return f"Metadata(title={self.title}, description={self.description}, access={self.access}, " \
               f"timestamp={self.timestamp}, formatted_date={self.formatted_date})"
