from pymongo import MongoClient
from bson import ObjectId
import re

client = None
db = None
meds_col = None
sales_col = None


class InsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class MockCursor:
    def __init__(self, docs):
        self._docs = docs
        self._results = list(docs)

    def sort(self, key, direction=1):
        reverse = direction == -1
        self._results.sort(key=lambda d: d.get(key), reverse=reverse)
        return self

    def limit(self, n):
        self._results = self._results[:n]
        return self

    def skip(self, n):
        self._results = self._results[n:]
        return self

    def __iter__(self):
        return iter(self._results)

    def __len__(self):
        return len(self._results)


class InMemoryCollection:
    def __init__(self):
        self._docs = []

    def drop(self):
        self._docs.clear()

    def insert_one(self, doc):
        if "_id" not in doc:
            doc = dict(doc)
            doc["_id"] = ObjectId()
        self._docs.append(doc)
        return InsertOneResult(doc["_id"])

    def _match(self, doc, query):
        if not query:
            return True
        # support expr for quantity <= min_quantity
        if "$expr" in query:
            expr = query["$expr"]
            if "$lte" in expr:
                left, right = expr["$lte"]
                if left == "$quantity" and right == "$min_quantity":
                    return doc.get("quantity", 0) <= doc.get("min_quantity", 0)
        # date range
        if "date" in query and isinstance(query["date"], dict):
            gte = query["date"].get("$gte")
            if gte is not None:
                return doc.get("date") >= gte
        # regex on name
        if "name" in query and isinstance(query["name"], dict):
            regex = query["name"].get("$regex")
            options = query["name"].get("$options", "")
            flags = re.IGNORECASE if "i" in options else 0
            return re.search(regex, doc.get("name", ""), flags) is not None
        # direct equality checks
        for k, v in query.items():
            # handle medication_id exact match
            if k in doc and doc.get(k) == v:
                continue
            # handle _id lookup by ObjectId
            if k == "_id" and isinstance(v, ObjectId):
                return doc.get("_id") == v
            # if key absent or not matching
            return False
        return True

    def find(self, query=None):
        query = query or {}
        results = [d for d in self._docs if self._match(d, query)]
        return MockCursor(results)

    def find_one(self, query):
        for d in self._docs:
            if self._match(d, query):
                return d
        return None

    def count_documents(self, query=None):
        query = query or {}
        return sum(1 for d in self._docs if self._match(d, query))

    def aggregate(self, pipeline):
        # support simple group sum/count for total and cnt
        if not pipeline:
            return []
        stage = pipeline[0]
        if "$group" in stage:
            total = 0
            cnt = 0
            for d in self._docs:
                total += d.get("total", 0)
                cnt += 1
            return [{"_id": None, "total": total, "cnt": cnt}]
        return []

    def distinct(self, key):
        return list({d.get(key) for d in self._docs if key in d})

    def update_one(self, filter_q, update):
        for d in self._docs:
            if self._match(d, filter_q):
                if "$set" in update:
                    for k, v in update["$set"].items():
                        d[k] = v
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        d[k] = d.get(k, 0) + v
                return

    def delete_one(self, filter_q):
        for i, d in enumerate(self._docs):
            if self._match(d, filter_q):
                del self._docs[i]
                return


def init_db(app):
    global client, db, meds_col, sales_col

    if app.config["USE_MOCK_DB"]:
        try:
            import mongomock

            client = mongomock.MongoClient()
            db = client[app.config["MONGO_DB"]]
            meds_col = db["medications"]
            sales_col = db["sales"]
            return
        except Exception:
            # Fallback to simple in-memory collections if mongomock or its
            # dependencies are not available in the environment.
            client = None
            db = {}
            meds_col = InMemoryCollection()
            sales_col = InMemoryCollection()
            return
    else:
        client = MongoClient(app.config["MONGO_URI"])
        db = client[app.config["MONGO_DB"]]
        meds_col = db["medications"]
        sales_col = db["sales"]
