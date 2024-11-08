import json


class SystemError:
    @classmethod
    def unmet_dependency(cls, **kwargs):
        message = kwargs["message"] if "message" in kwargs else "message not available!"
        details = kwargs["details"] if "details" in kwargs else None
        error = kwargs["error"] if "error" in kwargs else None
        extra = kwargs["extra"] if "extra" in kwargs else None

        print("===========================================================================")
        print("Error In Dependency: \n")

        if details is not None:
            print(json.dumps(
                {"message": message, "details": details}, indent=2))
        else:
            print(json.dumps({"message": message}, indent=2))

        if error is not None:
            print({"error": error})

        if extra is not None:
            if 'cls' in extra:
                try:
                    print(json.dumps({cls.__dict__}, indent=2),)
                except Exception as error:
                    print(error)
                    print.pprint({"extra": cls.__dict__}, indent=2)
            else:
                print({"extra": extra})

        print("===========================================================================")

        raise SystemExit
