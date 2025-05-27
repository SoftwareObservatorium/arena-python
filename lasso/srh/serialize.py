from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import pandas as pd

from arena.arena import output_as_string, op_as_string, target_as_string, to_string
from lasso.job.ignite import ClientSrmRepository


@dataclass(frozen=True)
class CellId:
    executionId: str
    abstractionId: str
    actionId: str
    arenaId: str
    sheetId: str
    systemId: str
    variantId: str
    adapterId: str
    x: int
    y: int
    type: Optional[str] = None

    def __eq__(self, other):
        if not isinstance(other, CellId):
            return False
        return (
            self.executionId == other.executionId and
            self.abstractionId == other.abstractionId and
            self.actionId == other.actionId and
            self.arenaId == other.arenaId and
            self.sheetId == other.sheetId and
            self.systemId == other.systemId and
            self.variantId == other.variantId and
            self.adapterId == other.adapterId and
            self.x == other.x and
            self.y == other.y and
            self.type == other.type
        )

    def __hash__(self):
        return hash((
            self.executionId,
            self.abstractionId,
            self.actionId,
            self.arenaId,
            self.sheetId,
            self.systemId,
            self.variantId,
            self.adapterId,
            self.x,
            self.y,
            self.type
        ))


@dataclass
class CellValue:
    value: Optional[str] = None
    rawValue: Optional[str] = None
    valueType: Optional[str] = None
    lastModified: datetime = field(default_factory=datetime.now)
    executionTime: int = 0


class SRHWriter:

    def __init__(self, srm_repository: ClientSrmRepository):
        self.srm_repository = srm_repository


    def store(self, arena_job, arena_id, list_of_cells):
        self.srm_repository.put_all(list_of_cells)

    def cell_to_insert_args(self, cell_id: CellId, cell_value: CellValue):
        # Format the datetime for SQL if needed
        if cell_value.lastModified is not None:
            if isinstance(cell_value.lastModified, str):
                last_modified_str = cell_value.lastModified
            else:
                last_modified_str = cell_value.lastModified.strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_modified_str = None

        return [
            cell_id.executionId,
            cell_id.abstractionId,
            cell_id.actionId,
            cell_id.arenaId,
            cell_id.sheetId,
            cell_id.systemId,
            cell_id.variantId,
            cell_id.adapterId,
            cell_id.x,
            cell_id.y,
            cell_id.type,

            cell_value.value,
            cell_value.rawValue,
            cell_value.valueType,
            last_modified_str,
            cell_value.executionTime,
        ]

    def store_srm(self, arena_job, arena_id, srm: pd.DataFrame):
        list_of_cells = []

        seen_sheets = []
        seen_code_units = []

        # FIXME store oracle sheet as well
        # FIXME store code coverage
        # FIXME store mutants
        for adapted_implementation in srm.columns:
            impl_id = adapted_implementation.cut.id

            if not impl_id in seen_code_units:
                # persist metrics (indexmeasures)
                found = next((i for i in arena_job['implementations'] if i['id'] == impl_id), None)
                for key, value in found.get("code", {}).get("measures", {}).items():
                    # sheet body
                    list_of_cells.append(self.cell_to_insert_args(CellId(
                        executionId=arena_job['executionId'],
                        abstractionId=arena_job['abstractionId'],
                        actionId=arena_job['actionId'],
                        arenaId=arena_id,
                        sheetId="indexmeasures",
                        systemId=adapted_implementation.cut.id,
                        variantId=adapted_implementation.cut.variant_id,
                        adapterId=adapted_implementation.adapter_id,
                        x=-1,
                        y=-1,
                        type=key
                    ), CellValue(
                        value=str(value),
                        #rawValue=str(test_invocation.test.parsed_sheet.sheet.body),
                        lastModified=datetime.now()
                    )))

                    # add
                    seen_code_units.append(impl_id)


            for executed_invocations in srm[adapted_implementation]:
                test_invocation = executed_invocations.invocations.test_invocation
                # Compose sheetId from test signature and invocation
                sheet_id = str(test_invocation)

                if not sheet_id in seen_sheets:
                    # sheet body
                    list_of_cells.append(self.cell_to_insert_args(CellId(
                        executionId=arena_job['executionId'],
                        abstractionId=arena_job['abstractionId'],
                        actionId=arena_job['actionId'],
                        arenaId=arena_id,
                        sheetId=sheet_id,
                        systemId="abstraction",
                        variantId="abstraction",
                        adapterId="abstraction",
                        x=-1,
                        y=-1,
                        type="stimulussheet"
                    ), CellValue(
                        value=str(test_invocation.test.parsed_sheet.sheet.body),
                        #rawValue=str(test_invocation.test.parsed_sheet.sheet.body),
                        lastModified=datetime.now()
                    )))
                    # interface
                    list_of_cells.append(self.cell_to_insert_args(CellId(
                        executionId=arena_job['executionId'],
                        abstractionId=arena_job['abstractionId'],
                        actionId=arena_job['actionId'],
                        arenaId=arena_id,
                        sheetId=sheet_id,
                        systemId="abstraction",
                        variantId="abstraction",
                        adapterId="abstraction",
                        x=-1,
                        y=-1,
                        type="interface"
                    ), CellValue(
                        value=str(test_invocation.test.parsed_sheet.sheet.interface_lql),
                        #rawValue=str(test_invocation.test.parsed_sheet.sheet.interface_lql),
                        lastModified=datetime.now()
                    )))

                    # add
                    seen_sheets.append(sheet_id)

                for executed_invocation in executed_invocations.executed_sequence:
                    row_id = executed_invocation.invocation.index

                    output = output_as_string(executed_invocation, adapted_implementation)
                    list_of_cells.append(self.cell_to_insert_args(CellId(
                        executionId=arena_job['executionId'],
                        abstractionId=arena_job['abstractionId'],
                        actionId=arena_job['actionId'],
                        arenaId=arena_id,
                        sheetId=sheet_id,
                        systemId=adapted_implementation.cut.id,
                        variantId=adapted_implementation.cut.variant_id,
                        adapterId=adapted_implementation.adapter_id,
                        x=0,
                        y=row_id,
                        type="value"
                    ), CellValue(
                        value=str(output),
                        rawValue=str(output),
                        lastModified=datetime.now()
                    )))

                    op = op_as_string(executed_invocation, adapted_implementation)
                    list_of_cells.append(self.cell_to_insert_args(CellId(
                        executionId=arena_job['executionId'],
                        abstractionId=arena_job['abstractionId'],
                        actionId=arena_job['actionId'],
                        arenaId=arena_id,
                        sheetId=sheet_id,
                        systemId=adapted_implementation.cut.id,
                        variantId=adapted_implementation.cut.variant_id,
                        adapterId=adapted_implementation.adapter_id,
                        x=1,
                        y=row_id,
                        type="op"
                    ), CellValue(
                        value=str(op),
                        rawValue=str(op),
                        lastModified=datetime.now()
                    )))

                    service = target_as_string(executed_invocation, adapted_implementation)
                    list_of_cells.append(self.cell_to_insert_args(CellId(
                        executionId=arena_job['executionId'],
                        abstractionId=arena_job['abstractionId'],
                        actionId=arena_job['actionId'],
                        arenaId=arena_id,
                        sheetId=sheet_id,
                        systemId=adapted_implementation.cut.id,
                        variantId=adapted_implementation.cut.variant_id,
                        adapterId=adapted_implementation.adapter_id,
                        x=2,
                        y=row_id,
                        type="service"
                    ), CellValue(
                        value=str(service),
                        rawValue=str(service),
                        lastModified=datetime.now()
                    )))

                    if len(executed_invocation.inputs) > 0:
                        for i in range(len(executed_invocation.inputs)):
                            input_param = to_string(
                                executed_invocation.inputs[i], adapted_implementation)
                            list_of_cells.append(self.cell_to_insert_args(CellId(
                                executionId=arena_job['executionId'],
                                abstractionId=arena_job['abstractionId'],
                                actionId=arena_job['actionId'],
                                arenaId=arena_id,
                                sheetId=sheet_id,
                                systemId=adapted_implementation.cut.id,
                                variantId=adapted_implementation.cut.variant_id,
                                adapterId=adapted_implementation.adapter_id,
                                x=3 + i,
                                y=row_id,
                                type="input_value"
                            ), CellValue(
                                value=str(input_param),
                                rawValue=str(input_param),
                                lastModified=datetime.now()
                            )))

        # Store the cells
        self.store(arena_job, arena_id, list_of_cells)
