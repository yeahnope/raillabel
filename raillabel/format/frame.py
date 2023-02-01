# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import decimal
import typing as t
import uuid
from dataclasses import dataclass, field

from .num import Num
from .object_data import ObjectData
from .stream_reference import StreamReference


@dataclass
class Frame:
    """A container of dynamic, timewise, information.

    Parameters
    ----------
    uid: int
        Number of the frame withing the annotation file. Must be unique.
    timestamp: decimal.Decimal
        Timestamp containing the Unix epoch time of the frame with up to nanosecond precision.
    streams: dict of raillabel.format.StreamReference, optional
        References to the streams with frame specific information like timestamp and uri.
        Default is {}.
    data: dict, optional
        Dictionary containing data directly connected to the frame and not to anny object.
        Dictionary keys are the ID-strings of the variable the data belongs to. Default is {}.
    objects: dict of raillabel.format.ObjectData, optional
        Dictionary containing the annotations per object. Dictionary keys are the object uids.
        Default is {}.

    Read-Only Attributes
    --------------------
    annotations: dict
        Dictionary containing all annotations of this frame, regardless of object or annotation
        type. Dictionary keys are annotation UIDs.
    """

    uid: int
    timestamp: decimal.Decimal = None
    streams: t.Dict[str, StreamReference] = field(default_factory=dict)
    data: t.Dict[str, Num] = field(default_factory=dict)
    objects: t.Dict[uuid.UUID, ObjectData] = field(default_factory=dict)

    @property
    def annotations(self) -> t.Dict[uuid.UUID, t.Any]:
        """Return dict containing all annotations of this frame.

        Dictionary keys are annotation UIDs.
        """
        annotations = {}
        for object in self.objects.values():
            for annotation_type in vars(object).values():
                if isinstance(annotation_type, dict):
                    annotations.update(annotation_type)

        return annotations

    def asdict(self) -> dict:
        """Export self as a dict compatible with the OpenLABEL schema.

        Returns
        -------
        dict_repr: dict
            Dict representation of this class instance.

        Raises
        ------
        ValueError
            if an attribute can not be converted to the type required by the OpenLabel schema.
        """

        dict_repr = {}

        if self.timestamp is not None or self.streams != {}:
            dict_repr["frame_properties"] = {}

        if self.timestamp is not None:
            dict_repr["frame_properties"]["timestamp"] = str(self.timestamp)

        if self.streams != {}:
            dict_repr["frame_properties"]["streams"] = {
                str(k): v.asdict() for k, v in self.streams.items()
            }

        if self.data != {}:
            dict_repr["frame_properties"]["frame_data"] = {
                "num": [v.asdict() for v in self.data.values()]
            }

        if self.objects != {}:
            dict_repr["objects"] = {str(k): v.asdict() for k, v in self.objects.items()}

        return dict_repr

    def __eq__(self, other) -> bool:
        """Handel equal comparisons."""

        if not hasattr(other, "__dict__"):
            return False

        if len(self.__dict__) != len(other.__dict__):
            return False

        for attr in self.__dict__:

            if type(getattr(self, attr)) == type(self):
                if getattr(self, attr).uid != getattr(other, attr).uid:
                    return False

            else:
                if getattr(self, attr) != getattr(other, attr):
                    return False

        return True
