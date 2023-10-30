from typing import List
from functools import cached_property
from pinecone_text.dense.base_dense_ecoder import BaseDenseEncoder

from .base import RecordEncoder
from canopy.knowledge_base.models import KBQuery, KBEncodedDocChunk, KBDocChunk
from canopy.models.data_models import Query


class DenseRecordEncoder(RecordEncoder):
    """
    DenseRecordEncoder is a subclass of RecordEncoder that encode text as a dense vector (list of floats).
    DenseRecordEncoder uses a BaseDenseEncoder from the Pinecone Text library to encode the text.
    for more information about the BaseDenseEncoder see: https://github.com/pinecone-io/pinecone-text
    """  # noqa: E501

    def __init__(self,
                 dense_encoder: BaseDenseEncoder,
                 **kwargs):
        """
        Initialize the encoder.

        Args:
            dense_encoder: A BaseDenseEncoder to encode the text.
            **kwargs: Additional arguments to pass to the RecordEncoder.
        """  # noqa: E501
        super().__init__(**kwargs)
        self._dense_encoder = dense_encoder

    def _encode_documents_batch(self,
                                documents: List[KBDocChunk]
                                ) -> List[KBEncodedDocChunk]:
        """
        Encode a batch of documents, takes a list of KBDocChunk and returns a list of KBEncodedDocChunk.
        The implementation of this method encodes documents serially, meaning that it encodes the documents one by one.

        Args:
            documents: A list of KBDocChunk to encode.
        Returns:
            encoded chunks: A list of KBEncodedDocChunk, where only the values field is populated (and sparse_values is None)
        """  # noqa: E501
        dense_values = self._dense_encoder.encode_documents([d.text for d in documents])
        return [KBEncodedDocChunk(**d.dict(), values=v) for d, v in
                zip(documents, dense_values)]

    def _encode_queries_batch(self, queries: List[Query]) -> List[KBQuery]:
        """
        Encode a batch of queries, takes a list of Query and returns a list of KBQuery.
        The implementation of this method encodes queries serially, meaning that it encodes the queries one by one.

        Args:
            queries: A list of Query to encode.
        Returns:
            encoded queries: A list of KBQuery, where only the values field is populated (and sparse_values is None)
        """  # noqa: E501
        dense_values = self._dense_encoder.encode_queries([q.text for q in queries])
        return [KBQuery(**q.dict(), values=v) for q, v in zip(queries, dense_values)]

    @cached_property
    def dimension(self) -> int:
        """
        for dense encoders, the dimension is the length of the vector returned by the encoder.
        Canopy will run a single word through the encoder to get the dimension, this will also validate that the encoder
        is working properly.

        Returns:
            dimension(int): the dimension of the encoder
        """  # noqa: E501
        return len(self._dense_encoder.encode_documents(["hello"])[0])

    async def _aencode_documents_batch(self,
                                       documents: List[KBDocChunk]
                                       ) -> List[KBEncodedDocChunk]:
        raise NotImplementedError

    async def _aencode_queries_batch(self, queries: List[Query]) -> List[KBQuery]:
        raise NotImplementedError
