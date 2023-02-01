# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from dataclasses import dataclass

from ._annotation import _Annotation
from .point3d import Point3d


@dataclass
class Poly3d(_Annotation):
    """Sequence of 3D points. Can either be a polygon or polyline.

    Parameters
    ----------
    uid: str
        This a string representing the unique universal identifier for the annotation.
    name: str
        Human readable name describing the annotation.
    points: list of raillabel.format.Point3d
        List of the 3d points that make up the polyline.
    closed: bool
        This parameter states, whether the polyline represents a closed shape (a polygon) or an
        open line.
    attributes: dict, optional
        Attributes of the annotation. Dict keys are the name str of the attribute, values are the
        attribute values. Default is {}.
    coordinate_system: raillabel.format.CoordinateSystem, optional
        A reference to the coordinate_system, this annotation is labeled in. Default is None.
    object_data: raillabel.format.ObjectData, optional
        ObjectData containing the Poly3d. Used for accessing higher level informations.
        Default is None.

    Parameters
    ----------
    uri: str
        URI to the file, which contains the annotated object.
    """

    points: t.List[Point3d] = None
    closed: bool = None

    _REQ_FIELDS = ["points", "closed"]

    @classmethod
    def fromdict(
        self,
        data_dict: dict,
        coordinate_systems: dict,
        object_data=None,
    ) -> t.Tuple["Poly3d", list]:
        """Generate a Bbox object from a dictionary in the OpenLABEL format.

        Parameters
        ----------
        data_dict: dict
            OpenLABEL format dictionary containing the data for the annotation.
        coordinate_systems: dict
            Dictionary containing all coordinate_systems for the scene.
        object_data: raillabel.format.ObjectData, optional
            ObjectData containing the Poly3d. Used for accessing higher level informations.
            Default is None.

        Returns
        -------
        annotation: Bbox
            Converted annotation.
        warnings: list of str
            List of non-critical errors, that have occurred during the conversion.
        """

        warnings = []  # list of warnings, that have occurred during the parsing

        # Parses the points
        points = []
        for i in range(0, len(data_dict["val"]), 3):
            points.append(
                Point3d(x=data_dict["val"][i], y=data_dict["val"][i + 1], z=data_dict["val"][i + 2])
            )

        # Creates the annotation with all mandatory properties
        annotation = Poly3d(
            uid=str(data_dict["uid"]),
            name=str(data_dict["name"]),
            closed=data_dict["closed"],
            points=points,
            object_data=object_data,
        )

        # Adds the optional properties
        if "coordinate_system" in data_dict and data_dict["coordinate_system"] != "":
            try:
                annotation.coordinate_system = coordinate_systems[data_dict["coordinate_system"]]

            except KeyError:
                warnings.append(
                    f"{data_dict['coordinate_system']} does not exist as a coordinate system, "
                    + f"but is referenced for the annotation {data_dict['uid']}."
                )

        # Adds the attributes
        if "attributes" in data_dict:

            annotation.attributes = {
                a["name"]: a["val"] for l in data_dict["attributes"].values() for a in l
            }

            # Saves the uri attribute as a class attribute
            if "uri" in annotation.attributes:
                annotation.uri = annotation.attributes["uri"]
                del annotation.attributes["uri"]

        return annotation, warnings

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

        dict_repr = self._annotation_required_fields_asdict()

        dict_repr["closed"] = bool(self.closed)
        dict_repr["val"] = []
        for point in self.points:
            dict_repr["val"].extend(point.asdict())

        dict_repr.update(self._annotation_optional_fields_asdict())

        return dict_repr

    def __eq__(self, __o: object) -> bool:
        """Compare this annotation with another one."""
        return super().equals(self, __o)
