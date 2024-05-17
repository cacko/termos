from .service_account import db


class NowdataDb(object):

    @property
    def root_ref(self):
        return db.reference(f"termo/")

    def nowdata(self, **kwds):
        print(kwds)
        child_node = "_".join([kwds.get("model"), kwds.get("location")])
        options_ref = self.root_ref.child(child_node)
        return options_ref.set(kwds)
