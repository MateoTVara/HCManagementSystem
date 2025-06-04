package com.hcmanagement.controller;

import com.hcmanagement.service.AppointmentExcelService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class AppointmentReportController {
    
    @Autowired
    private AppointmentExcelService appointmentExcelService;

    @PostMapping("/generate/appointments/excel")
    public ResponseEntity<byte[]> generateAppointmentsExcel(@RequestBody List<Map<String, Object>> appointments) throws Exception {
        byte[] excelBytes = appointmentExcelService.generateAppointmentsExcel(appointments);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDisposition(ContentDisposition.attachment().filename("citas.xlsx").build());

        return new ResponseEntity<>(excelBytes, headers, HttpStatus.OK);
    }

}
