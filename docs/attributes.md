# Supported attributes

These tables describe the attribute dictionaries shipped with the library. Type lookup checks Sentinel-1, Sentinel-2, Sentinel-3, then Sentinel-5P and returns the first matching type, regardless of the selected collection. Unknown attributes raise `ValueError`.

`Collection/Name`, `PublicationDate`, and `ModificationDate` are additionally recognized by the registry. Use temporal predicates for product date fields; see the [operator reference](reference/operators.md).

## Sentinel-1

| Name                              | Type             |
|-----------------------------------|------------------|
| `productType`                     | `String`         |
| `origin`                          | `String`         |
| `datatakeID`                      | `Integer`        |
| `timeliness`                      | `String`         |
| `coordinates`                     | `String`         |
| `cycleNumber`                     | `Integer`        |
| `orbitNumber`                     | `Integer`        |
| `sliceNumber`                     | `Integer`        |
| `totalSlices`                     | `Integer`        |
| `productClass`                    | `String`         |
| `processorName`                   | `String`         |
| `orbitDirection`                  | `String`         |
| `processingDate`                  | `DateTimeOffset` |
| `operationalMode`                 | `String`         |
| `processingLevel`                 | `String`         |
| `swathIdentifier`                 | `String`         |
| `processingCenter`                | `String`         |
| `processorVersion`                | `String`         |
| `segmentStartTime`                | `DateTimeOffset` |
| `sliceProductFlag`                | `Boolean`        |
| `platformShortName`               | `String`         |
| `productGeneration`               | `DateTimeOffset` |
| `processingBaseline`              | `String`         |
| `productComposition`              | `String`         |
| `instrumentShortName`             | `String`         |
| `relativeOrbitNumber`             | `Integer`        |
| `polarisationChannels`            | `String`         |
| `productConsolidation`            | `String`         |
| `platformSerialIdentifier`        | `String`         |
| `instrumentConfigurationID`       | `Integer`        |
| `startTimeFromAscendingNode`      | `Double`         |
| `completionTimeFromAscendingNode` | `Double`         |

## Sentinel-1-RTC

This dictionary exists in the source but is not included in `ALL_ATTRIBUTES`. RTC-only names, such as `authority` and `spatialResolution`, are not recognized unless present in another registered dictionary.

| Name                       | Type      |
|----------------------------|-----------|
| `productType`              | `String`  |
| `authority`                | `String`  |
| `orbitNumber`              | `Integer` |
| `orbitDirection`           | `String`  |
| `operationalMode`          | `String`  |
| `processingLevel`          | `String`  |
| `platformShortName`        | `String`  |
| `spatialResolution`        | `Integer` |
| `instrumentShortName`      | `String`  |
| `relativeOrbitNumber`      | `Integer` |
| `polarisationChannels`     | `String`  |
| `platformSerialIdentifier` | `String`  |

## Sentinel-2

| Name                       | Type             |
|----------------------------|------------------|
| `productType`              | `String`         |
| `origin`                   | `String`         |
| `tileId`                   | `String`         |
| `cloudCover`               | `Double`         |
| `coordinates`              | `String`         |
| `datastripId`              | `String`         |
| `orbitNumber`              | `Integer`        |
| `qualityInfo`              | `Integer`        |
| `qualityStatus`            | `String`         |
| `sourceProduct`            | `String`         |
| `processingDate`           | `DateTimeOffset` |
| `productGroupId`           | `String`         |
| `lastOrbitNumber`          | `Integer`        |
| `operationalMode`          | `String`         |
| `processingLevel`          | `String`         |
| `processingCenter`         | `String`         |
| `processorVersion`         | `String`         |
| `granuleIdentifier`        | `String`         |
| `platformShortName`        | `String`         |
| `processingBaseline`       | `String`         |
| `instrumentShortName`      | `String`         |
| `relativeOrbitNumber`      | `Integer`        |
| `illuminationZenithAngle`  | `Double`         |
| `sourceProductOriginDate`  | `String`         |
| `platformSerialIdentifier` | `String`         |

## Sentinel-3

| Name                       | Type             |
|----------------------------|------------------|
| `productType`              | `String`         |
| `landCover`                | `Double`         |
| `cloudCover`               | `Double`         |
| `timeliness`               | `String`         |
| `brightCover`              | `Double`         |
| `coordinates`              | `String`         |
| `cycleNumber`              | `Integer`        |
| `orbitNumber`              | `Integer`        |
| `coastalCover`             | `Double`         |
| `processorName`            | `String`         |
| `closedSeaCover`           | `Integer`        |
| `openOceanCover`           | `Integer`        |
| `orbitDirection`           | `String`         |
| `processingDate`           | `DateTimeOffset` |
| `snowOrIceCover`           | `Double`         |
| `lastOrbitNumber`          | `Integer`        |
| `operationalMode`          | `String`         |
| `processingLevel`          | `String`         |
| `processingCenter`         | `String`         |
| `processorVersion`         | `String`         |
| `salineWaterCover`         | `Double`         |
| `tidalRegionCover`         | `Double`         |
| `platformShortName`        | `String`         |
| `baselineCollection`       | `String`         |
| `lastOrbitDirection`       | `String`         |
| `processingBaseline`       | `String`         |
| `continentalIceCover`      | `Integer`        |
| `instrumentShortName`      | `String`         |
| `relativeOrbitNumber`      | `Integer`        |
| `freshInlandWaterCover`    | `Double`         |
| `lastRelativeOrbitNumber`  | `Integer`        |
| `platformSerialIdentifier` | `String`         |

## Sentinel-5P

| Name                       | Type             |
|----------------------------|------------------|
| `productType`             | `String`         |
| `doi`                      | `String`          |
| `identifier`               | `String`         |
| `coordinates`              | `String`         |
| `orbitNumber`              | `Integer`        |
| `productClass`             | `String`         |
| `processorName`            | `String`         |
| `qualityStatus`            | `String`         |
| `processingDate`           | `DateTimeOffset` |
| `processingMode`           | `String`         |
| `acquisitionType`          | `String`         |
| `processingLevel`          | `String`         |
| `parentIdentifier`         | `String`         |
| `processingCenter`         | `String`         |
| `processorVersion`         | `String`         |
| `platformShortName`        | `String`         |
| `baselineCollection`       | `String`         |
| `processingBaseline`       | `String`         |
| `instrumentShortName`      | `String`         |
| `platformSerialIdentifier` | `String`         |

## Additional Attributes

| Name                       | Type             |
|----------------------------|------------------|
| `Collection/Name`        | `String`         |
| `PublicationDate`        | `DateTimeOffset` |
| `ModificationDate`       | `DateTimeOffset` |
