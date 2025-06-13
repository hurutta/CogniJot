from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


@router.post("/")
async def random_text(request: Request):
    data = await request.json()
    text = data.get("text", "")
    unique = []

    if text is not None and len(text.strip()) > 10:
        vectorizer = CountVectorizer(stop_words='english')
        X = vectorizer.fit_transform([text])

        # Apply LDA
        lda = LatentDirichletAllocation(n_components=1, random_state=42)
        lda.fit(X)

        feature_names = vectorizer.get_feature_names_out()
        for topic in lda.components_:
            top_keywords = [feature_names[i] for i in topic.argsort()[-10:][::-1]]
            unique.extend(top_keywords)

    return JSONResponse({"tags": unique})
