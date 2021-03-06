from ucca import evaluation
from ucca.constructions import PRIMARY

from ..conversion.sdp import SdpConverter

EVAL_TYPES = (evaluation.LABELED, evaluation.UNLABELED)


def get_scores(s1, s2, eval_type, verbose):
    converter = SdpConverter()
    edges = [[e for g in converter.generate_graphs(s) for n in g.nodes for e in n.outgoing +
              ([SdpConverter.Edge(rel=SdpConverter.TOP, remote=False, head=g.root)] if n.is_top else [])]
             for s in (s1, s2)]
    if eval_type == evaluation.UNLABELED:
        for es in edges:
            for e in es:
                e.rel = None
    g, r = map(set, edges)
    res = evaluation.EvaluatorResults({PRIMARY: evaluation.SummaryStatistics(len(g & r), len(g - r), len(r - g))},
                                      default={PRIMARY.name: PRIMARY})
    if verbose:
        print("Evaluation type: (" + eval_type + ")")
        res.print()
    return res


def evaluate(guessed, ref, converter=None, verbose=False, eval_types=EVAL_TYPES, **kwargs):
    del kwargs
    if converter is not None:
        guessed = converter(guessed)
        ref = converter(ref)
    return SdpScores((eval_type, get_scores(guessed, ref, eval_type, verbose)) for eval_type in eval_types)


class SdpScores(evaluation.Scores):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "SDP"
        self.format = "sdp"
